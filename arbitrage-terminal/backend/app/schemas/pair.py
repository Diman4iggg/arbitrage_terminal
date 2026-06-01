from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import MarketType


class TradingPairRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    base_asset: str
    quote_asset: str
    market_type: MarketType
    enabled: bool
    created_at: datetime
    updated_at: datetime


class TradingPairUpdate(BaseModel):
    enabled: bool

