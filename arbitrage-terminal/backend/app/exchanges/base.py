from abc import ABC, abstractmethod

from app.schemas.ticker import FundingRate, Market, Ticker


class ExchangeAdapter(ABC):
    name: str
    exchange_type: str

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        """Return a normalized perpetual ticker for a symbol such as BTC/USDT."""

    @abstractmethod
    async def get_markets(self) -> list[Market]:
        """Return normalized perpetual markets supported by the exchange."""

    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        """Return the current funding rate when the exchange exposes it."""

    async def close(self) -> None:
        """Release network resources owned by the adapter."""

