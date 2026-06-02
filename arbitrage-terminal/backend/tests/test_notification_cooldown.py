from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NotificationLog, TradeWatch
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

    async def send_trade_watch(self, trade_watch: TradeWatch, reasons: list[str]) -> bool:
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


async def test_trade_watch_notification_has_independent_cooldown_keys(
    session: AsyncSession,
) -> None:
    sender = FakeSender()
    trade_watch = TradeWatch(
        symbol="BTC/USDT",
        buy_exchange="Binance",
        sell_exchange="Bybit",
        price_spread_percent=Decimal("0.20"),
        funding_spread_percent=Decimal("0.03"),
        price_alert_threshold_percent=Decimal("0.10"),
        funding_alert_threshold_percent=Decimal("0.01"),
    )
    session.add(trade_watch)
    await session.commit()

    service = NotificationService(session, sender)
    first_count = await service.notify_trade_watch(trade_watch, cooldown_seconds=300)
    await session.commit()
    second_count = await service.notify_trade_watch(trade_watch, cooldown_seconds=300)

    assert first_count == 2
    assert second_count == 0
    assert sender.calls == 1
