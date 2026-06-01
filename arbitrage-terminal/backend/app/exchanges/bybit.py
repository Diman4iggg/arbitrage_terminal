from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class BybitAdapter(CcxtPerpetualAdapter):
    name = "Bybit"
    exchange_id = "bybit"

