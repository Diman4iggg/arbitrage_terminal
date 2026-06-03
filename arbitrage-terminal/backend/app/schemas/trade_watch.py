from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


class TradeWatchCreate(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_entry_price: Decimal = Field(gt=0)
    sell_entry_price: Decimal = Field(gt=0)
    position_size_coins: Decimal = Field(gt=0)
    notifications_enabled: bool = True
    price_alert_threshold_percent: Decimal | None = None
    price_alert_condition: Literal["above", "below"] = "above"
    funding_alert_threshold_percent: Decimal | None = None
    funding_alert_condition: Literal["above", "below"] = "above"
    target_price_alert_value: Decimal | None = Field(default=None, gt=0)
    target_price_alert_condition: Literal["above", "below"] = "above"
    target_price_alert_source: Literal["buy", "sell"] = "buy"

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        symbol = value.strip().upper()
        return symbol if "/" in symbol else f"{symbol}/USDT"

    @model_validator(mode="after")
    def validate_exchanges(self) -> "TradeWatchCreate":
        if self.buy_exchange == self.sell_exchange:
            raise ValueError("Buy and sell exchanges must be different")
        return self


class TradeWatchUpdate(BaseModel):
    buy_exchange: str | None = None
    sell_exchange: str | None = None
    enabled: bool | None = None
    notifications_enabled: bool | None = None
    price_alert_threshold_percent: Decimal | None = None
    price_alert_condition: Literal["above", "below"] | None = None
    funding_alert_threshold_percent: Decimal | None = None
    funding_alert_condition: Literal["above", "below"] | None = None
    target_price_alert_value: Decimal | None = Field(default=None, gt=0)
    target_price_alert_condition: Literal["above", "below"] | None = None
    target_price_alert_source: Literal["buy", "sell"] | None = None
    buy_entry_price: Decimal | None = Field(default=None, gt=0)
    sell_entry_price: Decimal | None = Field(default=None, gt=0)
    position_size_coins: Decimal | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_exchanges(self) -> "TradeWatchUpdate":
        if (
            self.buy_exchange is not None
            and self.sell_exchange is not None
            and self.buy_exchange == self.sell_exchange
        ):
            raise ValueError("Buy and sell exchanges must be different")
        return self


class TradeWatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    buy_exchange: str
    sell_exchange: str
    enabled: bool
    notifications_enabled: bool
    buy_entry_price: Decimal | None
    sell_entry_price: Decimal | None
    position_size_coins: Decimal | None
    price_alert_threshold_percent: Decimal | None
    price_alert_condition: str
    funding_alert_threshold_percent: Decimal | None
    funding_alert_condition: str
    target_price_alert_value: Decimal | None
    target_price_alert_condition: str
    target_price_alert_source: str
    buy_price: Decimal | None
    sell_price: Decimal | None
    price_spread_percent: Decimal | None
    buy_funding_rate_percent: Decimal | None
    sell_funding_rate_percent: Decimal | None
    funding_spread_percent: Decimal | None
    pnl_usdt: Decimal | None
    pnl_percent: Decimal | None
    last_updated_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def entry_spread_percent(self) -> Decimal | None:
        if self.buy_entry_price is None or self.sell_entry_price is None:
            return None
        return ((self.sell_entry_price - self.buy_entry_price) / self.buy_entry_price) * Decimal(
            "100"
        )


class TradeWatchSpreadPoint(BaseModel):
    timestamp: datetime
    spread_percent: Decimal


class TradeWatchSpreadHistoryRead(BaseModel):
    trade_watch_id: int
    symbol: str
    buy_exchange: str
    sell_exchange: str
    points: list[TradeWatchSpreadPoint]
