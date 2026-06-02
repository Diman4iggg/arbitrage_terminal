from typing import Protocol

from app.db.models import TradeWatch
from app.schemas.opportunity import Opportunity


class NotificationSender(Protocol):
    channel: str

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        """Send one opportunity and report whether a notification was delivered."""

    async def send_trade_watch(self, trade_watch: TradeWatch, reasons: list[str]) -> bool:
        """Send an alert for a manually tracked spread."""


class NullNotificationSender:
    channel = "disabled"

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        return False

    async def send_trade_watch(self, trade_watch: TradeWatch, reasons: list[str]) -> bool:
        return False
