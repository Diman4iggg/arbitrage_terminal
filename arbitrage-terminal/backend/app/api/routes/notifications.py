from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db_session
from app.notifications.telegram import TelegramConfigurationError, TelegramSender
from app.schemas.notification import NotificationTestResult
from app.services.settings_service import SettingsService

router = APIRouter(tags=["notifications"])


@router.post("/notifications/test-telegram", response_model=NotificationTestResult)
async def test_telegram_notification(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationTestResult:
    runtime_settings = await SettingsService(session).get_runtime_settings()
    sender = TelegramSender(
        bot_token=settings.telegram_bot_token,
        chat_id=runtime_settings.telegram_chat_id or settings.telegram_chat_id,
    )
    try:
        delivered = await sender.send_test_message()
    except TelegramConfigurationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        await sender.close()

    if not delivered:
        raise HTTPException(
            status_code=502,
            detail="Telegram Bot API did not deliver the test message",
        )
    return NotificationTestResult(
        delivered=True,
        message="Telegram test notification delivered",
    )
