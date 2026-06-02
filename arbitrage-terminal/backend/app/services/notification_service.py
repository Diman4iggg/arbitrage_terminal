import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NotificationLog, TradeWatch
from app.notifications.base import NotificationSender
from app.schemas.opportunity import Opportunity

logger = logging.getLogger(__name__)


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
            try:
                delivered = await self.sender.send_opportunity(opportunity)
            except Exception as error:  # noqa: BLE001 - notifications must not stop monitoring
                logger.error(
                    "Failed to send %s notification for %s: %s",
                    self.sender.channel,
                    opportunity_key,
                    str(error) or error.__class__.__name__,
                )
                continue
            if delivered:
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

    async def notify_trade_watch(self, trade_watch: TradeWatch, cooldown_seconds: int) -> int:
        reasons = self._get_trade_watch_reasons(trade_watch)
        pending_reasons = [
            reason
            for reason in reasons
            if not await self._is_in_cooldown(
                self.build_trade_watch_key(trade_watch, reason),
                cooldown_seconds,
            )
        ]
        if not pending_reasons:
            return 0
        try:
            delivered = await self.sender.send_trade_watch(trade_watch, pending_reasons)
        except Exception as error:  # noqa: BLE001 - notifications must not stop monitoring
            logger.error(
                "Failed to send %s trade watch notification for %s: %s",
                self.sender.channel,
                trade_watch.id,
                str(error) or error.__class__.__name__,
            )
            return 0
        if not delivered:
            return 0

        for reason in pending_reasons:
            spread = (
                trade_watch.price_spread_percent
                if reason == "price_spread"
                else abs(trade_watch.funding_spread_percent or 0)
            )
            self.session.add(
                NotificationLog(
                    opportunity_key=self.build_trade_watch_key(trade_watch, reason),
                    symbol=trade_watch.symbol,
                    buy_exchange=trade_watch.buy_exchange,
                    sell_exchange=trade_watch.sell_exchange,
                    spread_percent=spread,
                    channel=self.sender.channel,
                )
            )
        return len(pending_reasons)

    @staticmethod
    def build_opportunity_key(opportunity: Opportunity) -> str:
        return ":".join(
            (opportunity.symbol, opportunity.buy_exchange, opportunity.sell_exchange)
        )

    @staticmethod
    def build_trade_watch_key(trade_watch: TradeWatch, reason: str) -> str:
        return f"trade-watch:{trade_watch.id}:{reason}"

    @staticmethod
    def _get_trade_watch_reasons(trade_watch: TradeWatch) -> list[str]:
        reasons: list[str] = []
        if (
            trade_watch.price_alert_threshold_percent is not None
            and trade_watch.price_spread_percent is not None
            and trade_watch.price_spread_percent >= trade_watch.price_alert_threshold_percent
        ):
            reasons.append("price_spread")
        if (
            trade_watch.funding_alert_threshold_percent is not None
            and trade_watch.funding_spread_percent is not None
            and abs(trade_watch.funding_spread_percent)
            >= trade_watch.funding_alert_threshold_percent
        ):
            reasons.append("funding_spread")
        return reasons
