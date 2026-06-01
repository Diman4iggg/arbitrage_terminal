from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import ExchangeHealth, ExchangeType


class ExchangeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    exchange_type: ExchangeType
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ExchangeUpdate(BaseModel):
    enabled: bool


class ExchangeStatusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exchange_name: str
    status: ExchangeHealth
    last_success_at: datetime | None
    last_error_at: datetime | None
    last_error_message: str | None


class ExchangeWithStatusRead(ExchangeRead):
    status: ExchangeHealth = ExchangeHealth.UNKNOWN
    last_success_at: datetime | None = None
    last_error_at: datetime | None = None
    last_error_message: str | None = None
