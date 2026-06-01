from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import ArbitrageOpportunity, PriceSnapshot
from app.schemas.chart import (
    PriceChartRead,
    PricePoint,
    SpreadChartRead,
    SpreadPoint,
    TopSpreadPoint,
)

router = APIRouter(tags=["charts"])


@router.get("/charts/prices", response_model=PriceChartRead)
async def get_price_chart(
    symbol: str,
    minutes: int = Query(default=30, ge=1, le=1440),
    session: AsyncSession = Depends(get_db_session),
) -> PriceChartRead:
    cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
    result = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == symbol.upper(), PriceSnapshot.timestamp >= cutoff)
        .order_by(PriceSnapshot.timestamp)
    )
    return PriceChartRead(
        symbol=symbol.upper(),
        points=[
            PricePoint(
                exchange=snapshot.exchange_name,
                timestamp=snapshot.timestamp,
                bid_price=snapshot.bid_price,
                ask_price=snapshot.ask_price,
                last_price=snapshot.last_price,
            )
            for snapshot in result.scalars()
        ],
    )


@router.get("/charts/spreads", response_model=SpreadChartRead)
async def get_spread_chart(
    symbol: str,
    minutes: int = Query(default=30, ge=1, le=1440),
    session: AsyncSession = Depends(get_db_session),
) -> SpreadChartRead:
    normalized_symbol = symbol.upper()
    cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
    result = await session.execute(
        select(PriceSnapshot)
        .where(PriceSnapshot.symbol == normalized_symbol, PriceSnapshot.timestamp >= cutoff)
        .order_by(PriceSnapshot.timestamp)
    )
    snapshots_by_bucket: dict[datetime, list[PriceSnapshot]] = defaultdict(list)
    for snapshot in result.scalars():
        timestamp = snapshot.timestamp
        bucket = timestamp.replace(second=(timestamp.second // 10) * 10, microsecond=0)
        snapshots_by_bucket[bucket].append(snapshot)

    points: list[SpreadPoint] = []
    for timestamp, snapshots in snapshots_by_bucket.items():
        latest_by_exchange = {snapshot.exchange_name: snapshot for snapshot in snapshots}
        if len(latest_by_exchange) < 2:
            continue
        buy_snapshot = min(latest_by_exchange.values(), key=lambda item: item.last_price)
        sell_snapshot = max(latest_by_exchange.values(), key=lambda item: item.last_price)
        if buy_snapshot.last_price <= 0:
            continue
        spread_percent = (
            (sell_snapshot.last_price - buy_snapshot.last_price) / buy_snapshot.last_price
        ) * Decimal("100")
        points.append(
            SpreadPoint(
                timestamp=timestamp,
                buy_exchange=buy_snapshot.exchange_name,
                sell_exchange=sell_snapshot.exchange_name,
                buy_price=buy_snapshot.last_price,
                sell_price=sell_snapshot.last_price,
                spread_percent=spread_percent,
            )
        )
    return SpreadChartRead(symbol=normalized_symbol, points=points)


@router.get("/charts/top-spreads", response_model=list[TopSpreadPoint])
async def get_top_spreads(
    minutes: int = Query(default=30, ge=1, le=1440),
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> list[TopSpreadPoint]:
    cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
    result = await session.execute(
        select(ArbitrageOpportunity)
        .where(ArbitrageOpportunity.detected_at >= cutoff)
        .order_by(ArbitrageOpportunity.spread_percent.desc())
        .limit(limit)
    )
    return [
        TopSpreadPoint(
            symbol=opportunity.symbol,
            buy_exchange=opportunity.buy_exchange,
            sell_exchange=opportunity.sell_exchange,
            spread_percent=opportunity.spread_percent,
            detected_at=opportunity.detected_at,
        )
        for opportunity in result.scalars()
    ]
