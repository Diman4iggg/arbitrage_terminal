from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.scheduler import reschedule_monitoring_job
from app.db.database import get_db_session
from app.schemas.settings import RuntimeSettings, RuntimeSettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter(tags=["settings"])


@router.get("/settings", response_model=RuntimeSettings)
async def get_settings(session: AsyncSession = Depends(get_db_session)) -> RuntimeSettings:
    return await SettingsService(session).get_runtime_settings()


@router.patch("/settings", response_model=RuntimeSettings)
async def update_settings(
    update: RuntimeSettingsUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> RuntimeSettings:
    runtime_settings = await SettingsService(session).update_runtime_settings(update)
    if update.update_interval_seconds is not None:
        reschedule_monitoring_job(runtime_settings.update_interval_seconds)
    return runtime_settings
