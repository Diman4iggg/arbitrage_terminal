from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import ArbitrageOpportunity, OpportunityStatus
from app.schemas.opportunity import OpportunityRead

router = APIRouter(tags=["opportunities"])


@router.get("/opportunities", response_model=list[OpportunityRead])
async def get_opportunities(
    symbol: str | None = None,
    exchange: str | None = None,
    min_spread: Decimal = Query(default=Decimal("0"), ge=0),
    status: OpportunityStatus | None = OpportunityStatus.ACTIVE,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
) -> list[ArbitrageOpportunity]:
    query = select(ArbitrageOpportunity).where(
        ArbitrageOpportunity.spread_percent >= min_spread
    )
    if symbol:
        query = query.where(ArbitrageOpportunity.symbol == symbol.upper())
    if exchange:
        query = query.where(
            or_(
                ArbitrageOpportunity.buy_exchange == exchange,
                ArbitrageOpportunity.sell_exchange == exchange,
            )
        )
    if status:
        query = query.where(ArbitrageOpportunity.status == status)
    result = await session.execute(
        query.order_by(ArbitrageOpportunity.spread_percent.desc()).limit(limit)
    )
    return list(result.scalars())
