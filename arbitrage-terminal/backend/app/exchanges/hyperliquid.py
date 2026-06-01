import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from time import monotonic
from typing import Any

import httpx

from app.db.models import MarketType
from app.exchanges.base import ExchangeAdapter
from app.schemas.ticker import FundingRate, Market, Ticker


class HyperliquidAdapter(ExchangeAdapter):
    name = "Hyperliquid"
    exchange_type = "perp_dex"

    def __init__(
        self,
        base_url: str = "https://api.hyperliquid.xyz",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(base_url=base_url, timeout=10.0)
        self._mids: dict[str, str] = {}
        self._mids_loaded_at = 0.0
        self._mids_lock = asyncio.Lock()

    async def _post_info(self, payload: dict[str, Any]) -> Any:
        for attempt in range(3):
            try:
                response = await self.client.post("/info", json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as error:
                if error.response.status_code != 429 and error.response.status_code < 500:
                    raise
                if attempt == 2:
                    raise
            except httpx.RequestError:
                if attempt == 2:
                    raise
            await asyncio.sleep(0.25 * (2**attempt))
        raise RuntimeError("Hyperliquid request retry loop exited unexpectedly")

    async def get_ticker(self, symbol: str) -> Ticker:
        coin = self._coin_from_symbol(symbol)
        mids = await self._get_all_mids()
        price = mids.get(coin)
        if price is None:
            raise ValueError(f"{self.name} does not support perpetual market {symbol}")
        return Ticker(
            exchange=self.name,
            symbol=symbol,
            market_type=MarketType.PERPETUAL,
            last_price=Decimal(str(price)),
            timestamp=datetime.now(UTC),
        )

    async def _get_all_mids(self) -> dict[str, str]:
        if monotonic() - self._mids_loaded_at < 1:
            return self._mids
        async with self._mids_lock:
            if monotonic() - self._mids_loaded_at >= 1:
                self._mids = await self._post_info({"type": "allMids"})
                self._mids_loaded_at = monotonic()
        return self._mids

    async def get_markets(self) -> list[Market]:
        metadata = await self._post_info({"type": "meta"})
        return [
            Market(
                exchange=self.name,
                symbol=f"{asset['name']}/USDT",
                base_asset=asset["name"],
                quote_asset="USDT",
                active=not asset.get("isDelisted", False),
            )
            for asset in metadata["universe"]
        ]

    async def get_funding_rate(self, symbol: str) -> FundingRate | None:
        coin = self._coin_from_symbol(symbol)
        metadata, contexts = await self._post_info({"type": "metaAndAssetCtxs"})
        for asset, context in zip(metadata["universe"], contexts, strict=True):
            if asset["name"] == coin and context.get("funding") is not None:
                return FundingRate(
                    exchange=self.name,
                    symbol=symbol,
                    rate=Decimal(str(context["funding"])),
                    timestamp=datetime.now(UTC),
                )
        return None

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    @staticmethod
    def _coin_from_symbol(symbol: str) -> str:
        base_asset, quote_asset = symbol.split("/", maxsplit=1)
        if quote_asset != "USDT":
            raise ValueError("Hyperliquid normalized perpetual symbols must use the USDT quote")
        return base_asset
