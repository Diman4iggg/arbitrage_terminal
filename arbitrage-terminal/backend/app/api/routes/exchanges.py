from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import Exchange, ExchangeHealth, ExchangeStatus
from app.schemas.exchange import ExchangeUpdate, ExchangeWithStatusRead

router = APIRouter(tags=["exchanges"])


@router.get("/exchanges", response_model=list[ExchangeWithStatusRead])
async def get_exchanges(
    session: AsyncSession = Depends(get_db_session),
) -> list[ExchangeWithStatusRead]:
    result = await session.execute(
        select(Exchange, ExchangeStatus)
        .outerjoin(ExchangeStatus, ExchangeStatus.exchange_name == Exchange.name)
        .order_by(Exchange.name)
    )
    return [_serialize_exchange(exchange, status) for exchange, status in result.all()]


@router.patch("/exchanges/{exchange_id}", response_model=ExchangeWithStatusRead)
async def update_exchange(
    exchange_id: int,
    update: ExchangeUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ExchangeWithStatusRead:
    exchange = await session.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    exchange.enabled = update.enabled
    await session.commit()
    await session.refresh(exchange)
    status_result = await session.execute(
        select(ExchangeStatus).where(ExchangeStatus.exchange_name == exchange.name)
    )
    return _serialize_exchange(exchange, status_result.scalar_one_or_none())


def _serialize_exchange(
    exchange: Exchange,
    status: ExchangeStatus | None,
) -> ExchangeWithStatusRead:
    return ExchangeWithStatusRead(
        id=exchange.id,
        name=exchange.name,
        slug=exchange.slug,
        exchange_type=exchange.exchange_type,
        enabled=exchange.enabled,
        created_at=exchange.created_at,
        updated_at=exchange.updated_at,
        status=status.status if status else ExchangeHealth.UNKNOWN,
        last_success_at=status.last_success_at if status else None,
        last_error_at=status.last_error_at if status else None,
        last_error_message=status.last_error_message if status else None,
    )
