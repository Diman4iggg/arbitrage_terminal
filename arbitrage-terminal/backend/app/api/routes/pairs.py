from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import MarketType, TradingPair
from app.schemas.pair import TradingPairCreate, TradingPairRead, TradingPairUpdate

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


@router.post("/pairs", response_model=TradingPairRead, status_code=status.HTTP_201_CREATED)
async def create_pair(
    payload: TradingPairCreate,
    session: AsyncSession = Depends(get_db_session),
) -> TradingPair:
    result = await session.execute(
        select(TradingPair).where(
            TradingPair.symbol == payload.symbol,
            TradingPair.market_type == MarketType.PERPETUAL,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Trading pair already exists")
    base_asset, quote_asset = payload.symbol.split("/", maxsplit=1)
    pair = TradingPair(
        symbol=payload.symbol,
        base_asset=base_asset,
        quote_asset=quote_asset,
        market_type=MarketType.PERPETUAL,
    )
    session.add(pair)
    await session.commit()
    await session.refresh(pair)
    return pair
