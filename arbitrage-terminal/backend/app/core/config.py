from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Arbitrage Terminal API"
    app_env: str = "development"
    app_debug: bool = False
    api_prefix: str = "/api"

    database_url: str = (
        "postgresql+asyncpg://arbitrage:change_me@localhost:5432/arbitrage_terminal"
    )
    cors_origins: str = "http://localhost:5173"

    market_type: str = "perpetual"
    scheduler_enabled: bool = True
    monitoring_interval_seconds: int = 10
    persist_price_snapshots: bool = True
    price_snapshot_retention_hours: int = 24
    default_spread_threshold_percent: float = 0.5
    notification_cooldown_seconds: int = 300

    telegram_notifications_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
