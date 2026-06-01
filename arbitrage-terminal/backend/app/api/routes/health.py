from typing import Literal

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import async_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, Literal["ok", "unavailable"]]:
    database_status: Literal["ok", "unavailable"] = "ok"

    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        database_status = "unavailable"

    return {"status": "ok", "database": database_status}

