from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class BitgetAdapter(CcxtPerpetualAdapter):
    name = "Bitget"
    exchange_id = "bitget"
