from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, select
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

    updates = payload.model_dump(exclude_unset=True)
    next_buy_exchange = updates.get("buy_exchange", trade_watch.buy_exchange)
    next_sell_exchange = updates.get("sell_exchange", trade_watch.sell_exchange)
    exchanges_changed = (
        next_buy_exchange != trade_watch.buy_exchange
        or next_sell_exchange != trade_watch.sell_exchange
    )

    if "buy_exchange" in updates or "sell_exchange" in updates:
        if next_buy_exchange == next_sell_exchange:
            raise HTTPException(
                status_code=422,
                detail="Buy and sell exchanges must be different",
            )
        await _validate_exchanges(session, next_buy_exchange, next_sell_exchange)

    for field, value in updates.items():
        setattr(trade_watch, field, value)

    if exchanges_changed:
        _clear_live_trade_watch_values(trade_watch)
        await session.execute(
            delete(TradeWatchSpreadSnapshot).where(
                TradeWatchSpreadSnapshot.trade_watch_id == trade_watch.id
            )
        )

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


def _clear_live_trade_watch_values(trade_watch: TradeWatch) -> None:
    trade_watch.buy_price = None
    trade_watch.sell_price = None
    trade_watch.price_spread_percent = None
    trade_watch.buy_funding_rate_percent = None
    trade_watch.sell_funding_rate_percent = None
    trade_watch.funding_spread_percent = None
    trade_watch.pnl_usdt = None
    trade_watch.pnl_percent = None
    trade_watch.last_updated_at = None
    trade_watch.last_error = None
