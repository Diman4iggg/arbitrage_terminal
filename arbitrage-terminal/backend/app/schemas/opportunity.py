from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.db.models import MarketType, OpportunityStatus


class Opportunity(BaseModel):
    symbol: str
    market_type: MarketType = MarketType.PERPETUAL
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    spread_percent: Decimal
    buy_funding_rate_percent: Decimal | None = None
    sell_funding_rate_percent: Decimal | None = None
    funding_spread_percent: Decimal | None = None
    detected_at: datetime
    status: OpportunityStatus = OpportunityStatus.ACTIVE


class OpportunityRead(Opportunity):
    model_config = ConfigDict(from_attributes=True)

    id: int
