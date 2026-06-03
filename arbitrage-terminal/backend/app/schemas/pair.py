from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, field_validator

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


class TradingPairCreate(BaseModel):
    symbol: str

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        symbol = value.strip().upper()
        normalized_symbol = symbol if "/" in symbol else f"{symbol}/USDT"
        base_asset, quote_asset = normalized_symbol.split("/", maxsplit=1)
        if not re.fullmatch(r"[A-Z0-9]{2,20}", base_asset):
            raise ValueError("Base asset must contain 2-20 uppercase letters or digits")
        if not base_asset or quote_asset != "USDT":
            raise ValueError("Perpetual monitoring pairs must use a base asset and the USDT quote")
        return normalized_symbol
