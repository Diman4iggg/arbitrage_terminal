from typing import Any

from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class BinanceAdapter(CcxtPerpetualAdapter):
    name = "Binance"
    exchange_id = "binance"

    def _client_config(self) -> dict[str, Any]:
        return {
            "enableRateLimit": True,
            "options": {"defaultType": "future"},
        }

