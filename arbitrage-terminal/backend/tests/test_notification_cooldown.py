from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NotificationLog
from app.notifications.telegram import TelegramSender
from app.schemas.opportunity import Opportunity
from app.services.notification_service import NotificationService
from tests.factories import make_opportunity


class FakeSender:
    channel = "test"

    def __init__(self) -> None:
        self.calls = 0

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        self.calls += 1
        return True


async def test_notification_cooldown_blocks_duplicate_delivery(session: AsyncSession) -> None:
    sender = FakeSender()
    service = NotificationService(session, sender)
    opportunity = make_opportunity()

    first_count = await service.notify_opportunities([opportunity], cooldown_seconds=300, enabled=True)
    second_count = await service.notify_opportunities([opportunity], cooldown_seconds=300, enabled=True)
    log_count = await session.scalar(select(func.count()).select_from(NotificationLog))

    assert first_count == 1
    assert second_count == 0
    assert sender.calls == 1
    assert log_count == 1


async def test_notification_errors_do_not_stop_monitoring(session: AsyncSession) -> None:
    sender = TelegramSender(bot_token="", chat_id="")
    try:
        count = await NotificationService(session, sender).notify_opportunities(
            [make_opportunity()],
            cooldown_seconds=300,
            enabled=True,
        )
    finally:
        await sender.close()

    assert count == 0

