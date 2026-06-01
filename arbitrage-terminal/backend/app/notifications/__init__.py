"""Notification sender contracts and integrations."""

from app.notifications.base import NotificationSender, NullNotificationSender

__all__ = ["NotificationSender", "NullNotificationSender"]
