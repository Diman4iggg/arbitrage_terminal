from fastapi import APIRouter, HTTPException

from app.schemas.notification import NotificationTestResult

router = APIRouter(tags=["notifications"])


@router.post("/notifications/test-telegram", response_model=NotificationTestResult)
async def test_telegram_notification() -> NotificationTestResult:
    raise HTTPException(
        status_code=501,
        detail="Telegram sender is introduced in Stage 6",
    )
