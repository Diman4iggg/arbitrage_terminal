from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NotificationLog
from app.notifications.base import NotificationSender
from app.schemas.opportunity import Opportunity


class NotificationService:
    def __init__(self, session: AsyncSession, sender: NotificationSender) -> None:
        self.session = session
        self.sender = sender

    async def notify_opportunities(
        self,
        opportunities: list[Opportunity],
        cooldown_seconds: int,
        enabled: bool,
    ) -> int:
        if not enabled:
            return 0

        sent_count = 0
        for opportunity in opportunities:
            opportunity_key = self.build_opportunity_key(opportunity)
            if await self._is_in_cooldown(opportunity_key, cooldown_seconds):
                continue
            if await self.sender.send_opportunity(opportunity):
                self.session.add(
                    NotificationLog(
                        opportunity_key=opportunity_key,
                        symbol=opportunity.symbol,
                        buy_exchange=opportunity.buy_exchange,
                        sell_exchange=opportunity.sell_exchange,
                        spread_percent=opportunity.spread_percent,
                        channel=self.sender.channel,
                    )
                )
                sent_count += 1

        if sent_count:
            await self.session.commit()
        return sent_count

    async def _is_in_cooldown(self, opportunity_key: str, cooldown_seconds: int) -> bool:
        cooldown_started_at = datetime.now(UTC) - timedelta(seconds=cooldown_seconds)
        result = await self.session.execute(
            select(NotificationLog.id)
            .where(
                NotificationLog.opportunity_key == opportunity_key,
                NotificationLog.sent_at >= cooldown_started_at,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def build_opportunity_key(opportunity: Opportunity) -> str:
        return ":".join(
            (opportunity.symbol, opportunity.buy_exchange, opportunity.sell_exchange)
        )

