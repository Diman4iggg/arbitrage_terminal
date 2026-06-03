from collections.abc import AsyncIterator

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.main import app


async def test_settings_can_disable_opportunity_notifications(
    session: AsyncSession,
) -> None:
    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            defaults = await client.get("/api/settings")
            updated = await client.patch(
                "/api/settings",
                json={"opportunity_notifications_enabled": False},
            )
            reloaded = await client.get("/api/settings")
    finally:
        app.dependency_overrides.clear()

    assert defaults.status_code == 200
    assert defaults.json()["opportunity_notifications_enabled"] is True
    assert updated.status_code == 200
    assert updated.json()["opportunity_notifications_enabled"] is False
    assert reloaded.json()["opportunity_notifications_enabled"] is False
