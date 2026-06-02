import asyncio
import logging
from decimal import Decimal

from app.exchanges.base import ExchangeAdapter
from app.schemas.opportunity import Opportunity
from app.schemas.ticker import FundingRate

logger = logging.getLogger(__name__)


class OpportunityFundingService:
    def __init__(self, adapters: dict[str, ExchangeAdapter]) -> None:
        self.adapters = adapters

    async def enrich(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        await asyncio.gather(*(self._enrich_opportunity(item) for item in opportunities))
        return opportunities

    async def _enrich_opportunity(self, opportunity: Opportunity) -> None:
        buy_adapter = self.adapters.get(opportunity.buy_exchange)
        sell_adapter = self.adapters.get(opportunity.sell_exchange)
        if buy_adapter is None or sell_adapter is None:
            return
        results = await asyncio.gather(
            buy_adapter.get_funding_rate(opportunity.symbol),
            sell_adapter.get_funding_rate(opportunity.symbol),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                logger.warning(
                    "Failed to fetch opportunity funding for %s: %s",
                    opportunity.symbol,
                    str(result) or result.__class__.__name__,
                )
        buy_rate = _funding_percent(results[0])
        sell_rate = _funding_percent(results[1])
        opportunity.buy_funding_rate_percent = buy_rate
        opportunity.sell_funding_rate_percent = sell_rate
        opportunity.funding_spread_percent = (
            sell_rate - buy_rate if buy_rate is not None and sell_rate is not None else None
        )


def _funding_percent(result: FundingRate | BaseException | None) -> Decimal | None:
    return result.rate * Decimal("100") if isinstance(result, FundingRate) else None
