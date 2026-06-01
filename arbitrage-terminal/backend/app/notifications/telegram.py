import html
import logging
from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.schemas.opportunity import Opportunity

logger = logging.getLogger(__name__)


class TelegramConfigurationError(ValueError):
    pass


class TelegramSender:
    channel = "telegram"

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.bot_token = bot_token.strip()
        self.chat_id = chat_id.strip()
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(timeout=10.0)

    @property
    def configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    async def send_opportunity(self, opportunity: Opportunity) -> bool:
        return await self.send_message(format_opportunity_message(opportunity))

    async def send_test_message(self) -> bool:
        detected_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        return await self.send_message(
            "<b>Arbitrage Terminal test</b>\n\n"
            "Telegram notifications are configured correctly.\n"
            f"Sent at: <code>{detected_at}</code>"
        )

    async def send_message(self, text: str) -> bool:
        if not self.configured:
            raise TelegramConfigurationError(
                "Telegram bot token and chat ID must be configured"
            )
        try:
            response = await self.client.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            response.raise_for_status()
            payload = response.json()
            if not payload.get("ok", False):
                logger.error("Telegram Bot API rejected the message: %s", payload.get("description"))
                return False
            return True
        except httpx.HTTPStatusError as error:
            logger.error(
                "Telegram Bot API returned HTTP %s",
                error.response.status_code,
            )
            return False
        except httpx.RequestError as error:
            logger.error("Telegram Bot API request failed: %s", error.__class__.__name__)
            return False

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()


def format_opportunity_message(opportunity: Opportunity) -> str:
    detected_at = opportunity.detected_at.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        "<b>Arbitrage opportunity</b>\n\n"
        f"Pair: <code>{html.escape(opportunity.symbol)} PERP</code>\n"
        f"Buy: <b>{html.escape(opportunity.buy_exchange)}</b> at "
        f"<code>{_format_decimal(opportunity.buy_price)}</code>\n"
        f"Sell: <b>{html.escape(opportunity.sell_exchange)}</b> at "
        f"<code>{_format_decimal(opportunity.sell_price)}</code>\n"
        f"Spread: <b>{opportunity.spread_percent:.2f}%</b>\n"
        f"Detected at: <code>{detected_at}</code>"
    )


def _format_decimal(value: Decimal) -> str:
    formatted = f"{value:f}"
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted
