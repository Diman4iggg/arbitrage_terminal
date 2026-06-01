from abc import ABC, abstractmethod
from decimal import Decimal

from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker


class Strategy(ABC):
    name: str

    @abstractmethod
    async def find_opportunities(
        self,
        tickers: list[Ticker],
        default_threshold_percent: Decimal,
        threshold_per_pair: dict[str, Decimal] | None = None,
    ) -> list[Opportunity]:
        """Find opportunities in normalized market data."""

