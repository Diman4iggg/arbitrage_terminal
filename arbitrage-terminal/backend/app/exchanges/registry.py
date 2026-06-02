from collections.abc import Callable

from app.exchanges.base import ExchangeAdapter
from app.exchanges.aster import AsterAdapter
from app.exchanges.bingx import BingxAdapter
from app.exchanges.bitget import BitgetAdapter
from app.exchanges.binance import BinanceAdapter
from app.exchanges.bybit import BybitAdapter
from app.exchanges.hyperliquid import HyperliquidAdapter
from app.exchanges.mexc import MexcAdapter
from app.exchanges.gateio import GateioAdapter
from app.exchanges.okx import OkxAdapter
from app.exchanges.variational_omni import VariationalOmniAdapter

AdapterFactory = Callable[[], ExchangeAdapter]

ADAPTER_FACTORIES: dict[str, AdapterFactory] = {
    "binance": BinanceAdapter,
    "bybit": BybitAdapter,
    "mexc": MexcAdapter,
    "hyperliquid": HyperliquidAdapter,
    "aster": AsterAdapter,
    "variational-omni": VariationalOmniAdapter,
    "bingx": BingxAdapter,
    "bitget": BitgetAdapter,
    "okx": OkxAdapter,
    "gateio": GateioAdapter,
}


def create_adapter(slug: str) -> ExchangeAdapter:
    try:
        return ADAPTER_FACTORIES[slug]()
    except KeyError as error:
        raise ValueError(f"Unsupported exchange adapter: {slug}") from error


def create_adapters(slugs: list[str] | None = None) -> list[ExchangeAdapter]:
    selected_slugs = slugs or list(ADAPTER_FACTORIES)
    return [create_adapter(slug) for slug in selected_slugs]
