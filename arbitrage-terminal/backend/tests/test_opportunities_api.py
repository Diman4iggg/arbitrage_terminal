from collections.abc import AsyncIterator
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import ArbitrageOpportunity, MarketType, OpportunityStatus
from app.main import app


async def test_get_opportunities_returns_active_rows_sorted_by_spread(
    session: AsyncSession,
) -> None:
    session.add_all(
        [
            _make_model("BTC/USDT", "0.75", OpportunityStatus.ACTIVE),
            _make_model("ETH/USDT", "1.25", OpportunityStatus.ACTIVE),
            _make_model("SOL/USDT", "2.00", OpportunityStatus.EXPIRED),
        ]
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/opportunities", params={"min_spread": "0.5"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["symbol"] for item in response.json()] == ["ETH/USDT", "BTC/USDT"]


async def test_get_opportunities_supports_partial_symbol_filter(session: AsyncSession) -> None:
    session.add_all(
        [
            _make_model("BTC/USDT", "0.75", OpportunityStatus.ACTIVE),
            _make_model("ETH/USDT", "1.25", OpportunityStatus.ACTIVE),
        ]
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/opportunities", params={"symbol": "btc"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["symbol"] for item in response.json()] == ["BTC/USDT"]


def _make_model(
    symbol: str,
    spread_percent: str,
    status: OpportunityStatus,
) -> ArbitrageOpportunity:
    return ArbitrageOpportunity(
        symbol=symbol,
        market_type=MarketType.PERPETUAL,
        buy_exchange="Binance",
        sell_exchange="Bybit",
        buy_price=Decimal("100"),
        sell_price=Decimal("101"),
        spread_percent=Decimal(spread_percent),
        status=status,
    )
