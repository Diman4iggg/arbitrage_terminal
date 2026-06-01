import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.db.database import async_session_factory
from app.exchanges.registry import create_adapters
from app.services.monitoring_service import MonitoringService
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")
monitoring_service: MonitoringService | None = None


async def start_scheduler() -> None:
    global monitoring_service

    if not settings.scheduler_enabled:
        logger.info("Monitoring scheduler is disabled")
        return
    if scheduler.running:
        return

    interval_seconds = settings.monitoring_interval_seconds
    try:
        async with async_session_factory() as session:
            runtime_settings = await SettingsService(session).get_runtime_settings()
            interval_seconds = runtime_settings.update_interval_seconds
    except Exception:  # noqa: BLE001 - scheduler can start with environment defaults
        logger.exception("Failed to load scheduler interval from database, using environment default")

    monitoring_service = MonitoringService(create_adapters())
    scheduler.add_job(
        monitoring_service.run_cycle,
        trigger="interval",
        seconds=interval_seconds,
        id="market-monitoring",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        next_run_time=datetime.now(UTC),
    )
    scheduler.start()
    logger.info(
        "Monitoring scheduler started with a %s second interval",
        interval_seconds,
    )


async def stop_scheduler() -> None:
    global monitoring_service

    if scheduler.running:
        scheduler.shutdown(wait=False)
    if monitoring_service is not None:
        await monitoring_service.close()
        monitoring_service = None
    logger.info("Monitoring scheduler stopped")


def reschedule_monitoring_job(interval_seconds: int) -> None:
    if scheduler.running and scheduler.get_job("market-monitoring") is not None:
        scheduler.reschedule_job(
            "market-monitoring",
            trigger="interval",
            seconds=interval_seconds,
        )
        logger.info("Monitoring scheduler interval changed to %s seconds", interval_seconds)
