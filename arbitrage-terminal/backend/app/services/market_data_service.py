import asyncio
import logging
from dataclasses import dataclass

from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import Ticker

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MarketDataResult:
    tickers: list[Ticker]
    errors: dict[str, str]


class MarketDataService:
    def __init__(self, adapters: list[ExchangeAdapter]) -> None:
        self.adapters = adapters

    async def fetch_tickers(self, symbols: list[str]) -> MarketDataResult:
        tasks = [
            self._fetch_ticker(adapter=adapter, symbol=symbol)
            for adapter in self.adapters
            for symbol in symbols
        ]
        results = await asyncio.gather(*tasks)
        tickers: list[Ticker] = []
        errors: dict[str, str] = {}
        for adapter_name, symbol, ticker, error_message in results:
            if ticker is not None:
                tickers.append(ticker)
            elif error_message is not None:
                errors[f"{adapter_name}:{symbol}"] = error_message
        return MarketDataResult(tickers=tickers, errors=errors)

    async def close(self) -> None:
        await asyncio.gather(*(adapter.close() for adapter in self.adapters), return_exceptions=True)

    @staticmethod
    async def _fetch_ticker(
        adapter: ExchangeAdapter,
        symbol: str,
    ) -> tuple[str, str, Ticker | None, str | None]:
        try:
            return adapter.name, symbol, await adapter.get_ticker(symbol), None
        except Exception as error:  # noqa: BLE001 - one failed exchange must not stop a cycle
            logger.warning("Failed to fetch %s ticker from %s: %s", symbol, adapter.name, error)
            return adapter.name, symbol, None, str(error)

