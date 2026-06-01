from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PricePoint(BaseModel):
    exchange: str
    timestamp: datetime
    bid_price: Decimal | None
    ask_price: Decimal | None
    last_price: Decimal


class PriceChartRead(BaseModel):
    symbol: str
    points: list[PricePoint]


class SpreadPoint(BaseModel):
    timestamp: datetime
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    spread_percent: Decimal


class SpreadChartRead(BaseModel):
    symbol: str
    points: list[SpreadPoint]


class TopSpreadPoint(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    spread_percent: Decimal
    detected_at: datetime
