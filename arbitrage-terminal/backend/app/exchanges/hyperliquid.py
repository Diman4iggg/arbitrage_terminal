from datetime import UTC, datetime
from decimal import Decimal
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

    async def _post_info(self, payload: dict[str, Any]) -> Any:
        response = await self.client.post("/info", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_ticker(self, symbol: str) -> Ticker:
        coin = self._coin_from_symbol(symbol)
        mids = await self._post_info({"type": "allMids"})
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

