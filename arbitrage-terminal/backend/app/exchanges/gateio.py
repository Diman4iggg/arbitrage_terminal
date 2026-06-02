from app.exchanges.ccxt_base import CcxtPerpetualAdapter


class GateioAdapter(CcxtPerpetualAdapter):
    name = "Gate.io"
    exchange_id = "gateio"
