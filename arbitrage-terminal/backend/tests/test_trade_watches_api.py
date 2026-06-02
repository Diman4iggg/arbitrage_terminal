from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import Exchange, ExchangeType, TradeWatch, TradeWatchSpreadSnapshot
from app.main import app


async def test_create_trade_watch_normalizes_short_symbol(session: AsyncSession) -> None:
    session.add_all(
        [
            Exchange(name="Binance", slug="binance", exchange_type=ExchangeType.CEX),
            Exchange(name="Bybit", slug="bybit", exchange_type=ExchangeType.CEX),
        ]
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/trade-watches",
                json={
                    "symbol": "btc",
                    "buy_exchange": "Binance",
                    "sell_exchange": "Bybit",
                    "buy_entry_price": 67000,
                    "sell_entry_price": 67500,
                    "position_size_coins": 0.25,
                    "price_alert_threshold_percent": 0.1,
                    "funding_alert_threshold_percent": 0.01,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["symbol"] == "BTC/USDT"
    assert response.json()["position_size_coins"] == "0.250000000000"
    assert response.json()["entry_spread_percent"] == "0.7462686567164179104477611940"


async def test_create_trade_watch_preserves_negative_entry_spread(session: AsyncSession) -> None:
    session.add_all(
        [
            Exchange(name="Binance", slug="binance", exchange_type=ExchangeType.CEX),
            Exchange(name="Bybit", slug="bybit", exchange_type=ExchangeType.CEX),
        ]
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/trade-watches",
                json={
                    "symbol": "btc",
                    "buy_exchange": "Binance",
                    "sell_exchange": "Bybit",
                    "buy_entry_price": 68000,
                    "sell_entry_price": 67500,
                    "position_size_coins": 0.25,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert Decimal(response.json()["entry_spread_percent"]) < 0


async def test_create_trade_watch_requires_position_inputs(session: AsyncSession) -> None:
    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/trade-watches",
                json={
                    "symbol": "btc",
                    "buy_exchange": "Binance",
                    "sell_exchange": "Bybit",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422


async def test_update_trade_watch_changes_threshold_and_position_size(
    session: AsyncSession,
) -> None:
    session.add_all(
        [
            Exchange(name="Binance", slug="binance", exchange_type=ExchangeType.CEX),
            Exchange(name="Bybit", slug="bybit", exchange_type=ExchangeType.CEX),
        ]
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/api/trade-watches",
                json={
                    "symbol": "btc",
                    "buy_exchange": "Binance",
                    "sell_exchange": "Bybit",
                    "buy_entry_price": 67000,
                    "sell_entry_price": 67500,
                    "position_size_coins": 0.25,
                },
            )
            response = await client.patch(
                f"/api/trade-watches/{created.json()['id']}",
                json={
                    "position_size_coins": 0.5,
                    "price_alert_threshold_percent": 0.2,
                    "funding_alert_threshold_percent": 0.03,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["position_size_coins"] == "0.500000000000"
    assert response.json()["price_alert_threshold_percent"] == "0.200000"
    assert response.json()["funding_alert_threshold_percent"] == "0.030000"


async def test_get_trade_watch_spread_history_returns_recorded_points(
    session: AsyncSession,
) -> None:
    trade_watch = TradeWatch(
        symbol="BTC/USDT",
        buy_exchange="Binance",
        sell_exchange="Bybit",
        buy_entry_price=Decimal("67000"),
        sell_entry_price=Decimal("67500"),
        position_size_coins=Decimal("0.25"),
    )
    session.add(trade_watch)
    await session.flush()
    session.add(
        TradeWatchSpreadSnapshot(
            trade_watch_id=trade_watch.id,
            spread_percent=Decimal("0.123"),
            timestamp=datetime.now(UTC),
        )
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/trade-watches/{trade_watch.id}/spread-history")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["points"][0]["spread_percent"] == "0.123000"
