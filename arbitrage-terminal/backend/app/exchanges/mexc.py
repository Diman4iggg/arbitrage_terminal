from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class MexcAdapter(CcxtPerpetualAdapter):
    name = "MEXC"
    exchange_id = "mexc"

