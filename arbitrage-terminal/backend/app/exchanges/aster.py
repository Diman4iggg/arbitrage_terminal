from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class AsterAdapter(CcxtPerpetualAdapter):
    name = "Aster"
    exchange_id = "aster"
    exchange_type = "perp_dex"
