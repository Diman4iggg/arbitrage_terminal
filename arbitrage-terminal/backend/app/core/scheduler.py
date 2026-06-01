import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.exchanges.registry import create_adapters
from app.services.monitoring_service import MonitoringService

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

    monitoring_service = MonitoringService(create_adapters())
    scheduler.add_job(
        monitoring_service.run_cycle,
        trigger="interval",
        seconds=settings.monitoring_interval_seconds,
        id="market-monitoring",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        next_run_time=datetime.now(UTC),
    )
    scheduler.start()
    logger.info(
        "Monitoring scheduler started with a %s second interval",
        settings.monitoring_interval_seconds,
    )


async def stop_scheduler() -> None:
    global monitoring_service

    if scheduler.running:
        scheduler.shutdown(wait=False)
    if monitoring_service is not None:
        await monitoring_service.close()
        monitoring_service = None
    logger.info("Monitoring scheduler stopped")

