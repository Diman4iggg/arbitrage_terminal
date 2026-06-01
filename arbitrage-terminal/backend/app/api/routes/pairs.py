from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import TradingPair
from app.schemas.pair import TradingPairRead, TradingPairUpdate

router = APIRouter(tags=["pairs"])


@router.get("/pairs", response_model=list[TradingPairRead])
async def get_pairs(session: AsyncSession = Depends(get_db_session)) -> list[TradingPair]:
    result = await session.execute(select(TradingPair).order_by(TradingPair.symbol))
    return list(result.scalars())


@router.patch("/pairs/{pair_id}", response_model=TradingPairRead)
async def update_pair(
    pair_id: int,
    update: TradingPairUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> TradingPair:
    pair = await session.get(TradingPair, pair_id)
    if pair is None:
        raise HTTPException(status_code=404, detail="Trading pair not found")
    pair.enabled = update.enabled
    await session.commit()
    await session.refresh(pair)
    return pair
