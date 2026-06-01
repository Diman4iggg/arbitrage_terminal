import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import async_session_factory
from app.db.models import Exchange, MarketType, TradingPair
from app.exchanges.base import ExchangeAdapter
from app.notifications.base import NullNotificationSender
from app.services.arbitrage_service import ArbitrageService
from app.services.market_data_service import MarketDataService
from app.services.monitoring_state import MonitoringState, monitoring_state
from app.services.notification_service import NotificationService
from app.services.persistence_service import PersistenceService
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(
        self,
        adapters: list[ExchangeAdapter],
        state: MonitoringState = monitoring_state,
    ) -> None:
        self.adapters = {adapter.name: adapter for adapter in adapters}
        self.state = state
        self.arbitrage_service = ArbitrageService()

    async def run_cycle(self) -> None:
        self.state.running = True
        self.state.last_started_at = datetime.now(UTC)
        self.state.last_error = None
        try:
            async with async_session_factory() as session:
                enabled_adapters, symbols = await self._load_monitoring_targets(session)
                market_data = await MarketDataService(enabled_adapters).fetch_tickers(symbols)
                runtime_settings = await SettingsService(session).get_runtime_settings()
                opportunities = await self.arbitrage_service.find_opportunities(
                    tickers=market_data.tickers,
                    default_threshold_percent=Decimal(
                        str(runtime_settings.default_spread_threshold_percent)
                    ),
                    threshold_per_pair={
                        symbol: Decimal(str(threshold))
                        for symbol, threshold in runtime_settings.threshold_per_pair.items()
                    },
                )
                await PersistenceService(session).save_market_cycle(
                    tickers=market_data.tickers,
                    opportunities=opportunities,
                    errors=market_data.errors,
                    exchange_names=[adapter.name for adapter in enabled_adapters],
                    persist_snapshots=settings.persist_price_snapshots,
                    snapshot_retention_hours=settings.price_snapshot_retention_hours,
                )
                await NotificationService(
                    session=session,
                    sender=NullNotificationSender(),
                ).notify_opportunities(
                    opportunities=opportunities,
                    cooldown_seconds=runtime_settings.notification_cooldown_seconds,
                    enabled=runtime_settings.telegram_notifications_enabled,
                )
                self.state.tickers = market_data.tickers
                self.state.opportunities = opportunities
                self.state.errors = market_data.errors
                self.state.last_completed_at = datetime.now(UTC)
                logger.info(
                    "Monitoring cycle completed: %s tickers, %s opportunities, %s errors",
                    len(market_data.tickers),
                    len(opportunities),
                    len(market_data.errors),
                )
        except Exception as error:  # noqa: BLE001 - scheduler must survive failed cycles
            self.state.last_error = str(error)
            logger.exception("Monitoring cycle failed")
        finally:
            self.state.running = False

    async def close(self) -> None:
        await MarketDataService(list(self.adapters.values())).close()

    async def _load_monitoring_targets(
        self,
        session: AsyncSession,
    ) -> tuple[list[ExchangeAdapter], list[str]]:
        enabled_exchanges_result = await session.execute(
            select(Exchange).where(Exchange.enabled.is_(True))
        )
        enabled_pairs_result = await session.execute(
            select(TradingPair).where(
                TradingPair.enabled.is_(True),
                TradingPair.market_type == MarketType.PERPETUAL,
            )
        )
        enabled_adapters = [
            self.adapters[exchange.name]
            for exchange in enabled_exchanges_result.scalars()
            if exchange.name in self.adapters
        ]
        symbols = [pair.symbol for pair in enabled_pairs_result.scalars()]
        return enabled_adapters, symbols
