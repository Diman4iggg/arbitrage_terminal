from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AppSetting
from app.schemas.settings import RuntimeSettings, RuntimeSettingsUpdate


class SettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_runtime_settings(self) -> RuntimeSettings:
        result = await self.session.execute(select(AppSetting))
        stored_settings = {item.key: item.value for item in result.scalars()}
        return RuntimeSettings(
            default_spread_threshold_percent=stored_settings.get(
                "default_spread_threshold_percent",
                settings.default_spread_threshold_percent,
            ),
            threshold_per_pair=stored_settings.get("threshold_per_pair", {}),
            update_interval_seconds=stored_settings.get(
                "update_interval_seconds",
                settings.monitoring_interval_seconds,
            ),
            telegram_notifications_enabled=stored_settings.get(
                "telegram_notifications_enabled",
                settings.telegram_notifications_enabled,
            ),
            opportunity_notifications_enabled=stored_settings.get(
                "opportunity_notifications_enabled",
                True,
            ),
            telegram_chat_id=stored_settings.get("telegram_chat_id", settings.telegram_chat_id),
            notification_cooldown_seconds=stored_settings.get(
                "notification_cooldown_seconds",
                settings.notification_cooldown_seconds,
            ),
        )

    async def update_runtime_settings(self, update: RuntimeSettingsUpdate) -> RuntimeSettings:
        updates = update.model_dump(exclude_none=True)
        for key, value in updates.items():
            await self._upsert(key, value)
        await self.session.commit()
        return await self.get_runtime_settings()

    async def _upsert(self, key: str, value: Any) -> None:
        result = await self.session.execute(select(AppSetting).where(AppSetting.key == key))
        item = result.scalar_one_or_none()
        if item is None:
            self.session.add(AppSetting(key=key, value=value))
        else:
            item.value = value
