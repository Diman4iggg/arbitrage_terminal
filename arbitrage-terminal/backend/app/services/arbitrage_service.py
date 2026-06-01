from decimal import Decimal

from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker
from app.strategies.base import Strategy
from app.strategies.price_spread import PriceSpreadStrategy


class ArbitrageService:
    def __init__(self, strategy: Strategy | None = None) -> None:
        self.strategy = strategy or PriceSpreadStrategy()

    async def find_opportunities(
        self,
        tickers: list[Ticker],
        default_threshold_percent: Decimal,
        threshold_per_pair: dict[str, Decimal] | None = None,
    ) -> list[Opportunity]:
        return await self.strategy.find_opportunities(
            tickers=tickers,
            default_threshold_percent=default_threshold_percent,
            threshold_per_pair=threshold_per_pair,
        )

