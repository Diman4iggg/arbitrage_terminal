from pydantic import BaseModel, Field


class RuntimeSettings(BaseModel):
    default_spread_threshold_percent: float = Field(default=0.5, ge=0)
    threshold_per_pair: dict[str, float] = Field(default_factory=dict)
    update_interval_seconds: int = Field(default=10, ge=1)
    telegram_notifications_enabled: bool = False
    opportunity_notifications_enabled: bool = True
    telegram_chat_id: str = ""
    notification_cooldown_seconds: int = Field(default=300, ge=0)


class RuntimeSettingsUpdate(BaseModel):
    default_spread_threshold_percent: float | None = Field(default=None, ge=0)
    threshold_per_pair: dict[str, float] | None = None
    update_interval_seconds: int | None = Field(default=None, ge=1)
    telegram_notifications_enabled: bool | None = None
    opportunity_notifications_enabled: bool | None = None
    telegram_chat_id: str | None = None
    notification_cooldown_seconds: int | None = Field(default=None, ge=0)
