import asyncio
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import TradeWatch, TradeWatchSpreadSnapshot
from app.exchanges.base import ExchangeAdapter
from app.notifications.base import NotificationSender
from app.schemas.ticker import FundingRate
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class TradeWatchService:
    def __init__(
        self,
        session: AsyncSession,
        adapters: dict[str, ExchangeAdapter],
        sender: NotificationSender,
    ) -> None:
        self.session = session
        self.adapters = adapters
        self.notification_service = NotificationService(session, sender)

    async def refresh_all(
        self,
        telegram_enabled: bool,
        cooldown_seconds: int,
    ) -> None:
        await self.session.execute(
            delete(TradeWatchSpreadSnapshot).where(
                TradeWatchSpreadSnapshot.timestamp
                < datetime.now(UTC) - timedelta(hours=settings.price_snapshot_retention_hours)
            )
        )
        result = await self.session.execute(select(TradeWatch).where(TradeWatch.enabled.is_(True)))
        watches = list(result.scalars())
        for watch in watches:
            await self._refresh_watch(watch, telegram_enabled, cooldown_seconds)
        await self.session.commit()

    async def _refresh_watch(
        self,
        watch: TradeWatch,
        telegram_enabled: bool,
        cooldown_seconds: int,
    ) -> None:
        buy_adapter = self.adapters.get(watch.buy_exchange)
        sell_adapter = self.adapters.get(watch.sell_exchange)
        if buy_adapter is None or sell_adapter is None:
            watch.last_error = "Selected exchange adapter is unavailable"
            return

        try:
            buy_ticker, sell_ticker = await asyncio.gather(
                buy_adapter.get_ticker(watch.symbol),
                sell_adapter.get_ticker(watch.symbol),
            )
            watch.buy_price = buy_ticker.last_price
            watch.sell_price = sell_ticker.last_price
            watch.price_spread_percent = _spread_percent(
                buy_ticker.last_price,
                sell_ticker.last_price,
            )
            watch.last_updated_at = datetime.now(UTC)
            self.session.add(
                TradeWatchSpreadSnapshot(
                    trade_watch_id=watch.id,
                    spread_percent=watch.price_spread_percent,
                    timestamp=watch.last_updated_at,
                )
            )
            if (
                watch.buy_entry_price is not None
                and watch.sell_entry_price is not None
                and watch.position_size_coins is not None
            ):
                watch.pnl_usdt = _pnl_usdt(
                    buy_entry_price=watch.buy_entry_price,
                    sell_entry_price=watch.sell_entry_price,
                    buy_price=buy_ticker.last_price,
                    sell_price=sell_ticker.last_price,
                    position_size_coins=watch.position_size_coins,
                )
                watch.pnl_percent = _pnl_percent(
                    pnl_usdt=watch.pnl_usdt,
                    buy_entry_price=watch.buy_entry_price,
                    sell_entry_price=watch.sell_entry_price,
                    position_size_coins=watch.position_size_coins,
                )
            else:
                watch.pnl_usdt = None
                watch.pnl_percent = None
        except Exception as error:  # noqa: BLE001 - one watch must not stop monitoring
            watch.last_error = str(error) or error.__class__.__name__
            logger.warning("Failed to refresh trade watch %s prices: %s", watch.id, watch.last_error)
            return

        funding_results = await asyncio.gather(
            buy_adapter.get_funding_rate(watch.symbol),
            sell_adapter.get_funding_rate(watch.symbol),
            return_exceptions=True,
        )
        funding_errors = [str(item) or item.__class__.__name__ for item in funding_results if isinstance(item, Exception)]
        buy_funding = funding_results[0] if isinstance(funding_results[0], FundingRate) else None
        sell_funding = funding_results[1] if isinstance(funding_results[1], FundingRate) else None
        watch.buy_funding_rate_percent = _funding_percent(buy_funding)
        watch.sell_funding_rate_percent = _funding_percent(sell_funding)
        watch.funding_spread_percent = (
            watch.sell_funding_rate_percent - watch.buy_funding_rate_percent
            if watch.buy_funding_rate_percent is not None
            and watch.sell_funding_rate_percent is not None
            else None
        )
        watch.last_error = "; ".join(funding_errors)[:2000] if funding_errors else None

        if telegram_enabled and watch.notifications_enabled:
            await self.notification_service.notify_trade_watch(watch, cooldown_seconds)


def _spread_percent(buy_price: Decimal, sell_price: Decimal) -> Decimal:
    return ((sell_price - buy_price) / buy_price) * Decimal("100")


def _funding_percent(funding_rate: FundingRate | None) -> Decimal | None:
    return None if funding_rate is None else funding_rate.rate * Decimal("100")


def _pnl_usdt(
    buy_entry_price: Decimal,
    sell_entry_price: Decimal,
    buy_price: Decimal,
    sell_price: Decimal,
    position_size_coins: Decimal,
) -> Decimal:
    long_pnl = buy_price - buy_entry_price
    short_pnl = sell_entry_price - sell_price
    return (long_pnl + short_pnl) * position_size_coins


def _pnl_percent(
    pnl_usdt: Decimal,
    buy_entry_price: Decimal,
    sell_entry_price: Decimal,
    position_size_coins: Decimal,
) -> Decimal:
    initial_gross_notional = (buy_entry_price + sell_entry_price) * position_size_coins
    return pnl_usdt / initial_gross_notional * Decimal("100")
