"""Public market data adapters for perpetual exchanges."""

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

__all__ = [
    "BinanceAdapter",
    "AsterAdapter",
    "BingxAdapter",
    "BitgetAdapter",
    "BybitAdapter",
    "ExchangeAdapter",
    "HyperliquidAdapter",
    "GateioAdapter",
    "MexcAdapter",
    "OkxAdapter",
    "VariationalOmniAdapter",
]
