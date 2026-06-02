from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class OkxAdapter(CcxtPerpetualAdapter):
    name = "OKX"
    exchange_id = "okx"
