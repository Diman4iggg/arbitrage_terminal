from datetime import UTC, datetime
from decimal import Decimal

from app.notifications.telegram import format_opportunity_message
from app.schemas.opportunity import Opportunity


def test_opportunity_message_preserves_integer_price_zeroes() -> None:
    message = format_opportunity_message(
        Opportunity(
            symbol="BTC/USDT",
            buy_exchange="Binance",
            sell_exchange="Bybit",
            buy_price=Decimal("68000"),
            sell_price=Decimal("68450"),
            spread_percent=Decimal("0.6617"),
            detected_at=datetime(2026, 5, 28, 12, 30, tzinfo=UTC),
        )
    )

    assert "<code>68000</code>" in message
    assert "<code>68450</code>" in message
    assert "<b>0.66%</b>" in message

