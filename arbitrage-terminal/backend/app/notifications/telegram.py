import html
import logging
from datetime import UTC, datetime
from decimal import Decimal

import httpx

from app.db.models import TradeWatch
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

    async def send_trade_watch(self, trade_watch: TradeWatch, reasons: list[str]) -> bool:
        return await self.send_message(format_trade_watch_message(trade_watch, reasons))

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
        f"Funding: <code>{_format_optional_percent(opportunity.buy_funding_rate_percent)}</code> "
        f"-> <code>{_format_optional_percent(opportunity.sell_funding_rate_percent)}</code>\n"
        f"Funding delta: <b>{_format_optional_percent(opportunity.funding_spread_percent)}</b>\n"
        f"Detected at: <code>{detected_at}</code>"
    )


def format_trade_watch_message(trade_watch: TradeWatch, reasons: list[str]) -> str:
    detected_at = (trade_watch.last_updated_at or datetime.now(UTC)).astimezone(UTC)
    reason_text = ", ".join(reason.replace("_", " ") for reason in reasons)
    return (
        "<b>My Trades alert</b>\n\n"
        f"Pair: <code>{html.escape(trade_watch.symbol)} PERP</code>\n"
        f"Direction: <b>{html.escape(trade_watch.buy_exchange)}</b> -> "
        f"<b>{html.escape(trade_watch.sell_exchange)}</b>\n"
        f"Entry spread: <b>{_format_optional_percent(_entry_spread_percent(trade_watch))}</b>\n"
        f"Price spread: <b>{_format_optional_percent(trade_watch.price_spread_percent)}</b>\n"
        f"Funding spread: <b>{_format_optional_percent(trade_watch.funding_spread_percent)}</b>\n"
        f"Position PnL: <b>{_format_optional_decimal(trade_watch.pnl_usdt)} USDT</b> "
        f"({_format_optional_percent(trade_watch.pnl_percent)})\n"
        f"Triggered by: <code>{html.escape(reason_text)}</code>\n"
        f"Detected at: <code>{detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</code>"
    )


def _format_decimal(value: Decimal) -> str:
    formatted = f"{value:f}"
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted


def _format_optional_percent(value: Decimal | None) -> str:
    return "n/a" if value is None else f"{value:.4f}%"


def _format_optional_decimal(value: Decimal | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _entry_spread_percent(trade_watch: TradeWatch) -> Decimal | None:
    if trade_watch.buy_entry_price is None or trade_watch.sell_entry_price is None:
        return None
    return (
        (trade_watch.sell_entry_price - trade_watch.buy_entry_price)
        / trade_watch.buy_entry_price
        * Decimal("100")
    )
