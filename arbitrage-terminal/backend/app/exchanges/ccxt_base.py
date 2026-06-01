import asyncio
import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import ccxt.async_support as ccxt

from app.db.models import MarketType
from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import FundingRate, Market, Ticker

logger = logging.getLogger(__name__)


class CcxtPerpetualAdapter(ExchangeAdapter):
    exchange_id: str
    exchange_type = "cex"

    def __init__(self) -> None:
        exchange_class = getattr(ccxt, self.exchange_id)
        self.client = exchange_class(self._client_config())
        self._markets_loaded = False
        self._markets_lock = asyncio.Lock()

    def _client_config(self) -> dict[str, Any]:
        return {
            "enableRateLimit": True,
            "options": {"defaultType": "swap"},
        }

    async def _ensure_markets(self) -> None:
        if self._markets_loaded:
            return
        async with self._markets_lock:
            if not self._markets_loaded:
                await self.client.load_markets()
                self._markets_loaded = True

    async def _resolve_symbol(self, symbol: str) -> str:
        await self._ensure_markets()
        base_asset, quote_asset = symbol.split("/", maxsplit=1)
        candidates = [
            market
            for market in self.client.markets.values()
            if market.get("swap")
            and market.get("base") == base_asset
            and market.get("quote") == quote_asset
            and market.get("active") is not False
        ]
        linear_candidates = [market for market in candidates if market.get("linear")]
        selected = next(iter(linear_candidates or candidates), None)
        if selected is None:
            raise ValueError(f"{self.name} does not support perpetual market {symbol}")
        return str(selected["symbol"])

    async def get_ticker(self, symbol: str) -> Ticker:
        exchange_symbol = await self._resolve_symbol(symbol)
        ticker = await self.client.fetch_ticker(exchange_symbol)
        last_price = ticker.get("last")
        if last_price is None:
            raise ValueError(f"{self.name} returned no last price for {symbol}")
        return Ticker(
            exchange=self.name,
            symbol=symbol,
            market_type=MarketType.PERPETUAL,
            bid_price=_optional_decimal(ticker.get("bid")),
            ask_price=_optional_decimal(ticker.get("ask")),
            last_price=Decimal(str(last_price)),
            timestamp=_timestamp_to_datetime(ticker.get("timestamp")),
        )

    async def get_markets(self) -> list[Market]:
        await self._ensure_markets()
        markets: list[Market] = []
        for market in self.client.markets.values():
            if not market.get("swap") or not market.get("linear"):
                continue
            base_asset = market.get("base")
            quote_asset = market.get("quote")
            if not base_asset or not quote_asset:
                continue
            markets.append(
                Market(
                    exchange=self.name,
                    symbol=f"{base_asset}/{quote_asset}",
                    base_asset=base_asset,
                    quote_asset=quote_asset,
                    active=market.get("active") is not False,
                )
            )
        return markets

    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        if not self.client.has.get("fetchFundingRate"):
            return None
        exchange_symbol = await self._resolve_symbol(symbol)
        funding = await self.client.fetch_funding_rate(exchange_symbol)
        rate = funding.get("fundingRate")
        if rate is None:
            return None
        return FundingRate(
            exchange=self.name,
            symbol=symbol,
            rate=Decimal(str(rate)),
            timestamp=_timestamp_to_datetime(funding.get("timestamp")),
            next_funding_at=_optional_timestamp_to_datetime(funding.get("nextFundingTimestamp")),
        )

    async def close(self) -> None:
        await self.client.close()


def _optional_decimal(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _timestamp_to_datetime(timestamp: int | float | None) -> datetime:
    if timestamp is None:
        return datetime.now(UTC)
    return datetime.fromtimestamp(timestamp / 1000, tz=UTC)


def _optional_timestamp_to_datetime(timestamp: int | float | None) -> datetime | None:
    return None if timestamp is None else _timestamp_to_datetime(timestamp)
