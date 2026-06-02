from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import Exchange, TradeWatch, TradeWatchSpreadSnapshot
from app.schemas.trade_watch import (
    TradeWatchCreate,
    TradeWatchRead,
    TradeWatchSpreadHistoryRead,
    TradeWatchSpreadPoint,
    TradeWatchUpdate,
)

router = APIRouter(tags=["trade watches"])


@router.get("/trade-watches", response_model=list[TradeWatchRead])
async def get_trade_watches(
    session: AsyncSession = Depends(get_db_session),
) -> list[TradeWatch]:
    result = await session.execute(select(TradeWatch).order_by(TradeWatch.created_at.desc()))
    return list(result.scalars())


@router.post("/trade-watches", response_model=TradeWatchRead, status_code=status.HTTP_201_CREATED)
async def create_trade_watch(
    payload: TradeWatchCreate,
    session: AsyncSession = Depends(get_db_session),
) -> TradeWatch:
    await _validate_exchanges(session, payload.buy_exchange, payload.sell_exchange)
    trade_watch = TradeWatch(**payload.model_dump())
    session.add(trade_watch)
    await session.commit()
    await session.refresh(trade_watch)
    return trade_watch


@router.get(
    "/trade-watches/{trade_watch_id}/spread-history",
    response_model=TradeWatchSpreadHistoryRead,
)
async def get_trade_watch_spread_history(
    trade_watch_id: int,
    minutes: int = Query(default=30, ge=1, le=1440),
    session: AsyncSession = Depends(get_db_session),
) -> TradeWatchSpreadHistoryRead:
    trade_watch = await session.get(TradeWatch, trade_watch_id)
    if trade_watch is None:
        raise HTTPException(status_code=404, detail="Trade watch not found")
    cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
    result = await session.execute(
        select(TradeWatchSpreadSnapshot)
        .where(
            TradeWatchSpreadSnapshot.trade_watch_id == trade_watch_id,
            TradeWatchSpreadSnapshot.timestamp >= cutoff,
        )
        .order_by(TradeWatchSpreadSnapshot.timestamp)
    )
    return TradeWatchSpreadHistoryRead(
        trade_watch_id=trade_watch.id,
        symbol=trade_watch.symbol,
        buy_exchange=trade_watch.buy_exchange,
        sell_exchange=trade_watch.sell_exchange,
        points=[
            TradeWatchSpreadPoint(
                timestamp=snapshot.timestamp,
                spread_percent=snapshot.spread_percent,
            )
            for snapshot in result.scalars()
        ],
    )


@router.patch("/trade-watches/{trade_watch_id}", response_model=TradeWatchRead)
async def update_trade_watch(
    trade_watch_id: int,
    payload: TradeWatchUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> TradeWatch:
    trade_watch = await session.get(TradeWatch, trade_watch_id)
    if trade_watch is None:
        raise HTTPException(status_code=404, detail="Trade watch not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(trade_watch, field, value)
    await session.commit()
    await session.refresh(trade_watch)
    return trade_watch


@router.delete("/trade-watches/{trade_watch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade_watch(
    trade_watch_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    trade_watch = await session.get(TradeWatch, trade_watch_id)
    if trade_watch is None:
        raise HTTPException(status_code=404, detail="Trade watch not found")
    await session.delete(trade_watch)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _validate_exchanges(
    session: AsyncSession,
    buy_exchange: str,
    sell_exchange: str,
) -> None:
    result = await session.execute(
        select(Exchange.name).where(Exchange.name.in_([buy_exchange, sell_exchange]))
    )
    known_exchanges = set(result.scalars())
    missing = {buy_exchange, sell_exchange} - known_exchanges
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown exchange: {', '.join(sorted(missing))}",
        )
