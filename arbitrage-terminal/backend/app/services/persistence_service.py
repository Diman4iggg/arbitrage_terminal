from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ArbitrageOpportunity,
    ExchangeHealth,
    ExchangeStatus,
    OpportunityStatus,
    PriceSnapshot,
)
from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker


class PersistenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_market_cycle(
        self,
        tickers: list[Ticker],
        opportunities: list[Opportunity],
        errors: dict[str, str],
        exchange_names: list[str],
        persist_snapshots: bool,
        snapshot_retention_hours: int,
    ) -> None:
        if persist_snapshots:
            await self._prune_snapshots(snapshot_retention_hours)
            self._save_snapshots(tickers)
        await self._replace_active_opportunities(opportunities)
        await self._update_exchange_statuses(tickers, errors, exchange_names)
        await self.session.commit()

    def _save_snapshots(self, tickers: list[Ticker]) -> None:
        self.session.add_all(
            PriceSnapshot(
                exchange_name=ticker.exchange,
                symbol=ticker.symbol,
                market_type=ticker.market_type,
                bid_price=ticker.bid_price,
                ask_price=ticker.ask_price,
                last_price=ticker.last_price,
                timestamp=ticker.timestamp,
            )
            for ticker in tickers
        )

    async def _prune_snapshots(self, retention_hours: int) -> None:
        oldest_timestamp = datetime.now(UTC) - timedelta(hours=retention_hours)
        await self.session.execute(
            delete(PriceSnapshot).where(PriceSnapshot.timestamp < oldest_timestamp)
        )

    async def _replace_active_opportunities(self, opportunities: list[Opportunity]) -> None:
        await self.session.execute(
            update(ArbitrageOpportunity)
            .where(ArbitrageOpportunity.status == OpportunityStatus.ACTIVE)
            .values(status=OpportunityStatus.EXPIRED)
        )
        self.session.add_all(
            ArbitrageOpportunity(
                symbol=opportunity.symbol,
                market_type=opportunity.market_type,
                buy_exchange=opportunity.buy_exchange,
                sell_exchange=opportunity.sell_exchange,
                buy_price=opportunity.buy_price,
                sell_price=opportunity.sell_price,
                spread_percent=opportunity.spread_percent,
                buy_funding_rate_percent=opportunity.buy_funding_rate_percent,
                sell_funding_rate_percent=opportunity.sell_funding_rate_percent,
                funding_spread_percent=opportunity.funding_spread_percent,
                detected_at=opportunity.detected_at,
                status=opportunity.status,
            )
            for opportunity in opportunities
        )

    async def _update_exchange_statuses(
        self,
        tickers: list[Ticker],
        errors: dict[str, str],
        exchange_names: list[str],
    ) -> None:
        now = datetime.now(UTC)
        successful_exchanges = {ticker.exchange for ticker in tickers}
        errors_by_exchange: dict[str, list[str]] = {}
        for key, message in errors.items():
            exchange_name, _, symbol = key.partition(":")
            errors_by_exchange.setdefault(exchange_name, []).append(f"{symbol}: {message}")

        for exchange_name in exchange_names:
            status = await self._get_or_create_exchange_status(exchange_name)
            exchange_errors = errors_by_exchange.get(exchange_name, [])
            if exchange_name in successful_exchanges:
                status.last_success_at = now
            if exchange_errors:
                status.last_error_at = now
                status.last_error_message = "; ".join(exchange_errors)[:2000]
            if exchange_name in successful_exchanges:
                status.status = ExchangeHealth.ONLINE
                if not exchange_errors:
                    status.last_error_message = None
            elif exchange_errors:
                status.status = ExchangeHealth.ERROR
            else:
                status.status = ExchangeHealth.OFFLINE

    async def _get_or_create_exchange_status(self, exchange_name: str) -> ExchangeStatus:
        result = await self.session.execute(
            select(ExchangeStatus).where(ExchangeStatus.exchange_name == exchange_name)
        )
        status = result.scalar_one_or_none()
        if status is None:
            status = ExchangeStatus(exchange_name=exchange_name)
            self.session.add(status)
        return status
