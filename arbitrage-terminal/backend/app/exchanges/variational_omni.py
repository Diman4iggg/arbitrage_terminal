import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from time import monotonic
from typing import Any

import httpx

from app.db.models import MarketType
from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import FundingRate, Market, Ticker


class VariationalOmniAdapter(ExchangeAdapter):
    name = "Variational Omni"
    exchange_type = "perp_dex"

    def __init__(
        self,
        base_url: str = "https://omni-client-api.prod.ap-northeast-1.variational.io",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(base_url=base_url, timeout=10.0)
        self._listings: dict[str, dict[str, Any]] = {}
        self._listings_loaded_at = 0.0
        self._listings_lock = asyncio.Lock()

    async def _get_listings(self) -> dict[str, dict[str, Any]]:
        if monotonic() - self._listings_loaded_at < 3:
            return self._listings
        async with self._listings_lock:
            if monotonic() - self._listings_loaded_at >= 3:
                response = await self.client.get("/metadata/stats")
                response.raise_for_status()
                self._listings = {
                    str(item["ticker"]).upper(): item
                    for item in response.json()["listings"]
                }
                self._listings_loaded_at = monotonic()
        return self._listings

    async def get_ticker(self, symbol: str) -> Ticker:
        listing = await self._get_listing(symbol)
        quotes = listing.get("quotes", {})
        size_quote = quotes.get("size_1k", {})
        return Ticker(
            exchange=self.name,
            symbol=symbol,
            market_type=MarketType.PERPETUAL,
            bid_price=_optional_decimal(size_quote.get("bid")),
            ask_price=_optional_decimal(size_quote.get("ask")),
            last_price=Decimal(str(listing["mark_price"])),
            timestamp=_parse_timestamp(quotes.get("updated_at")),
        )

    async def get_markets(self) -> list[Market]:
        return [
            Market(
                exchange=self.name,
                symbol=f"{ticker}/USDT",
                base_asset=ticker,
                quote_asset="USDT",
            )
            for ticker in await self._get_listings()
        ]

    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        listing = await self._get_listing(symbol)
        rate = listing.get("funding_rate")
        if rate is None:
            return None
        return FundingRate(
            exchange=self.name,
            symbol=symbol,
            rate=Decimal(str(rate)),
            timestamp=datetime.now(UTC),
        )

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def _get_listing(self, symbol: str) -> dict[str, Any]:
        base_asset, quote_asset = symbol.split("/", maxsplit=1)
        if quote_asset != "USDT":
            raise ValueError("Variational Omni normalized symbols must use the USDT quote")
        listing = (await self._get_listings()).get(base_asset)
        if listing is None:
            raise ValueError(f"{self.name} does not support perpetual market {symbol}")
        return listing


def _optional_decimal(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
