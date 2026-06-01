from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.db.models import MarketType


class Ticker(BaseModel):
    exchange: str
    symbol: str
    market_type: MarketType = MarketType.PERPETUAL
    bid_price: Decimal | None = None
    ask_price: Decimal | None = None
    last_price: Decimal
    timestamp: datetime


class Market(BaseModel):
    exchange: str
    symbol: str
    base_asset: str
    quote_asset: str
    market_type: MarketType = MarketType.PERPETUAL
    active: bool = True


class FundingRate(BaseModel):
    exchange: str
    symbol: str
    rate: Decimal
    timestamp: datetime
    next_funding_at: datetime | None = None

