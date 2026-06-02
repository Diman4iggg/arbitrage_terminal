from decimal import Decimal

import pytest

from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import FundingRate, Market, Ticker
from app.services.market_data_service import MarketDataService
from tests.factories import make_ticker


class MockAdapter(ExchangeAdapter):
    name = "Mock"
    exchange_type = "cex"

    async def get_ticker(self, symbol: str) -> Ticker:
        if symbol == "FAIL/USDT":
            raise ValueError("unsupported pair")
        return make_ticker(self.name, "100", symbol=symbol)

    async def get_markets(self) -> list[Market]:
        return []

    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        return None


@pytest.mark.asyncio
async def test_market_data_service_keeps_successful_tickers_when_one_pair_fails() -> None:
    result = await MarketDataService([MockAdapter()]).fetch_tickers(
        ["BTC/USDT", "FAIL/USDT"]
    )

    assert len(result.tickers) == 1
    assert result.tickers[0].last_price == Decimal("100")
    assert result.errors == {"Mock:FAIL/USDT": "unsupported pair"}

