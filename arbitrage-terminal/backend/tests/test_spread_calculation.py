from decimal import Decimal

import pytest

from app.strategies.price_spread import PriceSpreadStrategy
from tests.factories import make_ticker


def test_calculate_opportunity_uses_lowest_buy_and_highest_sell_price() -> None:
    opportunity = PriceSpreadStrategy.calculate_opportunity(
        [
            make_ticker("Binance", "68000"),
            make_ticker("Bybit", "68450"),
            make_ticker("MEXC", "68100"),
        ]
    )

    assert opportunity is not None
    assert opportunity.buy_exchange == "Binance"
    assert opportunity.sell_exchange == "Bybit"
    assert opportunity.spread_percent == Decimal("0.6617647058823529411764705882")


def test_calculate_opportunity_requires_two_exchanges() -> None:
    assert PriceSpreadStrategy.calculate_opportunity([make_ticker("Binance", "68000")]) is None


@pytest.mark.asyncio
async def test_find_opportunities_applies_default_and_pair_thresholds() -> None:
    strategy = PriceSpreadStrategy()
    tickers = [
        make_ticker("Binance", "68000"),
        make_ticker("Bybit", "68450"),
        make_ticker("Binance", "3500", symbol="ETH/USDT"),
        make_ticker("Bybit", "3510", symbol="ETH/USDT"),
    ]

    opportunities = await strategy.find_opportunities(
        tickers=tickers,
        default_threshold_percent=Decimal("0.5"),
        threshold_per_pair={"BTC/USDT": Decimal("0.7")},
    )

    assert opportunities == []


@pytest.mark.asyncio
async def test_find_opportunities_returns_spreads_above_threshold_descending() -> None:
    opportunities = await PriceSpreadStrategy().find_opportunities(
        tickers=[
            make_ticker("Binance", "100", symbol="BTC/USDT"),
            make_ticker("Bybit", "101", symbol="BTC/USDT"),
            make_ticker("Binance", "100", symbol="ETH/USDT"),
            make_ticker("Bybit", "102", symbol="ETH/USDT"),
        ],
        default_threshold_percent=Decimal("0.5"),
    )

    assert [item.symbol for item in opportunities] == ["ETH/USDT", "BTC/USDT"]

