from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class BingxAdapter(CcxtPerpetualAdapter):
    name = "BingX"
    exchange_id = "bingx"
