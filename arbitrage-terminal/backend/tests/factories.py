from datetime import UTC, datetime
from decimal import Decimal

from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker


def make_ticker(
    exchange: str,
    price: str,
    symbol: str = "BTC/USDT",
) -> Ticker:
    return Ticker(
        exchange=exchange,
        symbol=symbol,
        last_price=Decimal(price),
        timestamp=datetime(2026, 6, 1, 12, 30, tzinfo=UTC),
    )


def make_opportunity(symbol: str = "BTC/USDT") -> Opportunity:
    return Opportunity(
        symbol=symbol,
        buy_exchange="Binance",
        sell_exchange="Bybit",
        buy_price=Decimal("68000"),
        sell_price=Decimal("68450"),
        spread_percent=Decimal("0.6617"),
        detected_at=datetime(2026, 6, 1, 12, 30, tzinfo=UTC),
    )

