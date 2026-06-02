from datetime import UTC, datetime
from decimal import Decimal

from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import FundingRate, Market, Ticker
from app.services.opportunity_funding_service import OpportunityFundingService
from tests.factories import make_opportunity


class FundingAdapter(ExchangeAdapter):
    exchange_type = "cex"

    def __init__(self, name: str, rate: str | None = None, error: Exception | None = None) -> None:
        self.name = name
        self.rate = rate
        self.error = error

    async def get_ticker(self, symbol: str) -> Ticker:
        raise NotImplementedError

    async def get_markets(self) -> list[Market]:
        return []

    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        if self.error:
            raise self.error
        if self.rate is None:
            return None
        return FundingRate(
            exchange=self.name,
            symbol=symbol,
            rate=Decimal(self.rate),
            timestamp=datetime.now(UTC),
        )


async def test_enrich_opportunity_adds_directional_funding_delta() -> None:
    opportunity = make_opportunity()

    await OpportunityFundingService(
        {
            "Binance": FundingAdapter("Binance", "0.0001"),
            "Bybit": FundingAdapter("Bybit", "0.0003"),
        }
    ).enrich([opportunity])

    assert opportunity.buy_funding_rate_percent == Decimal("0.01")
    assert opportunity.sell_funding_rate_percent == Decimal("0.03")
    assert opportunity.funding_spread_percent == Decimal("0.02")


async def test_enrich_opportunity_keeps_spread_when_one_funding_request_fails() -> None:
    opportunity = make_opportunity()

    await OpportunityFundingService(
        {
            "Binance": FundingAdapter("Binance", error=ValueError("funding unavailable")),
            "Bybit": FundingAdapter("Bybit", "0.0003"),
        }
    ).enrich([opportunity])

    assert opportunity.spread_percent == Decimal("0.6617")
    assert opportunity.buy_funding_rate_percent is None
    assert opportunity.sell_funding_rate_percent == Decimal("0.03")
    assert opportunity.funding_spread_percent is None
