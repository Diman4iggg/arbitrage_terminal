from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.db.models import (
    Exchange,
    ExchangeType,
    MarketType,
    PriceSnapshot,
    TradeWatch,
    TradeWatchSpreadSnapshot,
)
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
                    "price_alert_threshold_percent": -0.1,
                    "price_alert_condition": "below",
                    "funding_alert_threshold_percent": 0.01,
                    "funding_alert_condition": "above",
                    "target_price_alert_value": 67000,
                    "target_price_alert_condition": "above",
                    "target_price_alert_source": "buy",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["symbol"] == "BTC/USDT"
    assert response.json()["position_size_coins"] == "0.250000000000"
    assert response.json()["price_alert_threshold_percent"] == "-0.100000"
    assert response.json()["price_alert_condition"] == "below"
    assert response.json()["funding_alert_condition"] == "above"
    assert response.json()["target_price_alert_value"] == "67000.000000000000"
    assert response.json()["target_price_alert_condition"] == "above"
    assert response.json()["target_price_alert_source"] == "buy"
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
                    "buy_entry_price": 66000,
                    "sell_entry_price": 66660,
                    "position_size_coins": 0.5,
                    "price_alert_threshold_percent": -0.2,
                    "price_alert_condition": "below",
                    "funding_alert_threshold_percent": 1,
                    "funding_alert_condition": "above",
                    "target_price_alert_value": 67000,
                    "target_price_alert_condition": "above",
                    "target_price_alert_source": "sell",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["buy_entry_price"] == "66000.000000000000"
    assert response.json()["sell_entry_price"] == "66660.000000000000"
    assert response.json()["entry_spread_percent"] == "1.00"
    assert response.json()["position_size_coins"] == "0.500000000000"
    assert response.json()["price_alert_threshold_percent"] == "-0.200000"
    assert response.json()["price_alert_condition"] == "below"
    assert response.json()["funding_alert_threshold_percent"] == "1.000000"
    assert response.json()["funding_alert_condition"] == "above"
    assert response.json()["target_price_alert_value"] == "67000.000000000000"
    assert response.json()["target_price_alert_condition"] == "above"
    assert response.json()["target_price_alert_source"] == "sell"


async def test_update_trade_watch_changes_exchanges_and_resets_live_state(
    session: AsyncSession,
) -> None:
    session.add_all(
        [
            Exchange(name="Binance", slug="binance", exchange_type=ExchangeType.CEX),
            Exchange(name="Bybit", slug="bybit", exchange_type=ExchangeType.CEX),
            Exchange(name="OKX", slug="okx", exchange_type=ExchangeType.CEX),
            Exchange(name="Bitget", slug="bitget", exchange_type=ExchangeType.CEX),
        ]
    )
    trade_watch = TradeWatch(
        symbol="BTC/USDT",
        buy_exchange="Binance",
        sell_exchange="Bybit",
        buy_entry_price=Decimal("67000"),
        sell_entry_price=Decimal("67500"),
        position_size_coins=Decimal("0.25"),
        buy_price=Decimal("67100"),
        sell_price=Decimal("67600"),
        price_spread_percent=Decimal("0.745"),
        price_alert_threshold_percent=Decimal("0.1"),
    )
    session.add(trade_watch)
    await session.flush()
    session.add(
        TradeWatchSpreadSnapshot(
            trade_watch_id=trade_watch.id,
            spread_percent=Decimal("0.745"),
            timestamp=datetime.now(UTC),
        )
    )
    await session.commit()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db_session] = override_db_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.patch(
                f"/api/trade-watches/{trade_watch.id}",
                json={
                    "buy_exchange": "OKX",
                    "sell_exchange": "Bitget",
                    "price_alert_threshold_percent": 0.25,
                },
            )
            history = await client.get(f"/api/trade-watches/{trade_watch.id}/spread-history")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["buy_exchange"] == "OKX"
    assert response.json()["sell_exchange"] == "Bitget"
    assert response.json()["price_alert_threshold_percent"] == "0.250000"
    assert response.json()["buy_price"] is None
    assert response.json()["sell_price"] is None
    assert response.json()["price_spread_percent"] is None
    assert history.json()["points"] == []


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
    session.add(
        TradeWatchSpreadSnapshot(
            trade_watch_id=trade_watch.id,
            spread_percent=Decimal("9.999"),
            timestamp=datetime.now(UTC) - timedelta(days=2),
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
    assert len(response.json()["points"]) == 1
    assert response.json()["points"][0]["spread_percent"] == "0.123000"


async def test_trade_watch_spread_history_uses_price_snapshots_before_trade_creation(
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
    timestamp = datetime.now(UTC) - timedelta(hours=2)
    session.add_all(
        [
            trade_watch,
            PriceSnapshot(
                exchange_name="Binance",
                symbol="BTC/USDT",
                market_type=MarketType.PERPETUAL,
                last_price=Decimal("100"),
                timestamp=timestamp,
            ),
            PriceSnapshot(
                exchange_name="Bybit",
                symbol="BTC/USDT",
                market_type=MarketType.PERPETUAL,
                last_price=Decimal("101"),
                timestamp=timestamp,
            ),
        ]
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
    assert Decimal(response.json()["points"][0]["spread_percent"]) == Decimal("1")
