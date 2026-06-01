from typing import Protocol

from app.schemas.opportunity import Opportunity


class NotificationSender(Protocol):
    channel: str

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        """Send one opportunity and report whether a notification was delivered."""


class NullNotificationSender:
    channel = "disabled"

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        return False

