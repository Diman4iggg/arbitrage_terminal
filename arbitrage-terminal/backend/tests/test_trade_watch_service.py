from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.db.models import TradeWatch, TradeWatchSpreadSnapshot
from app.exchanges.base import ExchangeAdapter
from app.notifications.base import NullNotificationSender
from app.schemas.ticker import FundingRate, Market, Ticker
from app.services.trade_watch_service import TradeWatchService


class WatchAdapter(ExchangeAdapter):
    exchange_type = "cex"

    def __init__(self, name: str, price: str, funding_rate: str) -> None:
        self.name = name
        self.price = Decimal(price)
        self.funding_rate = Decimal(funding_rate)

    async def get_ticker(self, symbol: str) -> Ticker:
        return Ticker(
            exchange=self.name,
            symbol=symbol,
            last_price=self.price,
            timestamp=datetime.now(UTC),
        )

    async def get_markets(self) -> list[Market]:
        return []

    async def get_funding_rate(self, symbol: str) -> FundingRate:
        return FundingRate(
            exchange=self.name,
            symbol=symbol,
            rate=self.funding_rate,
            timestamp=datetime.now(UTC),
        )


async def test_refresh_trade_watch_calculates_directional_price_and_funding_spreads(
    session: AsyncSession,
) -> None:
    trade_watch = TradeWatch(
        symbol="BTC/USDT",
        buy_exchange="Buy",
        sell_exchange="Sell",
        buy_entry_price=Decimal("99"),
        sell_entry_price=Decimal("102"),
        position_size_coins=Decimal("2"),
    )
    session.add(trade_watch)
    await session.commit()

    await TradeWatchService(
        session=session,
        adapters={
            "Buy": WatchAdapter("Buy", "100", "0.0001"),
            "Sell": WatchAdapter("Sell", "101", "0.0003"),
        },
        sender=NullNotificationSender(),
    ).refresh_all(telegram_enabled=False, cooldown_seconds=300)

    assert trade_watch.buy_price == Decimal("100")
    assert trade_watch.sell_price == Decimal("101")
    assert trade_watch.price_spread_percent == Decimal("1")
    assert trade_watch.buy_funding_rate_percent == Decimal("0.01")
    assert trade_watch.sell_funding_rate_percent == Decimal("0.03")
    assert trade_watch.funding_spread_percent == Decimal("0.02")
    assert trade_watch.pnl_usdt == Decimal("4")
    assert trade_watch.pnl_percent == Decimal("4") / Decimal("402") * Decimal("100")
    assert trade_watch.last_error is None
    snapshot_count = await session.scalar(select(func.count()).select_from(TradeWatchSpreadSnapshot))
    assert snapshot_count == 1
