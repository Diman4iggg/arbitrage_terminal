from collections.abc import AsyncIterator

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.main import app


async def test_create_pair_normalizes_short_symbol(session: AsyncSession) -> None:
    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/pairs", json={"symbol": "sei"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["symbol"] == "SEI/USDT"
    assert response.json()["enabled"] is True


async def test_create_pair_rejects_non_usdt_quote(session: AsyncSession) -> None:
    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/pairs", json={"symbol": "BTC/USDC"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
