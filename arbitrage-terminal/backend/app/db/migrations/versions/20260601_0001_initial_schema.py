"""Initial market monitoring schema.

Revision ID: 20260601_0001
Revises:
Create Date: 2026-06-01
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260601_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


exchange_type = postgresql.ENUM("CEX", "PERP_DEX", name="exchange_type", create_type=False)
market_type = postgresql.ENUM("SPOT", "FUTURES", "PERPETUAL", name="market_type", create_type=False)
opportunity_status = postgresql.ENUM(
    "ACTIVE", "EXPIRED", name="opportunity_status", create_type=False
)
exchange_health = postgresql.ENUM(
    "UNKNOWN", "ONLINE", "OFFLINE", "ERROR", name="exchange_health", create_type=False
)


def upgrade() -> None:
    exchange_type.create(op.get_bind(), checkfirst=True)
    market_type.create(op.get_bind(), checkfirst=True)
    opportunity_status.create(op.get_bind(), checkfirst=True)
    exchange_health.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=50), nullable=False, unique=True),
        sa.Column("exchange_type", exchange_type, nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_exchanges_slug", "exchanges", ["slug"])

    op.create_table(
        "trading_pairs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("base_asset", sa.String(length=30), nullable=False),
        sa.Column("quote_asset", sa.String(length=30), nullable=False),
        sa.Column("market_type", market_type, nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_trading_pairs_symbol_market_type", "trading_pairs", ["symbol", "market_type"], unique=True)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False, unique=True),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_app_settings_key", "app_settings", ["key"])

    op.create_table(
        "arbitrage_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("market_type", market_type, nullable=False),
        sa.Column("buy_exchange", sa.String(length=50), nullable=False),
        sa.Column("sell_exchange", sa.String(length=50), nullable=False),
        sa.Column("buy_price", sa.Numeric(30, 12), nullable=False),
        sa.Column("sell_price", sa.Numeric(30, 12), nullable=False),
        sa.Column("spread_percent", sa.Numeric(12, 6), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", opportunity_status, nullable=False),
    )
    op.create_index("ix_opportunities_detected_at", "arbitrage_opportunities", ["detected_at"])
    op.create_index("ix_opportunities_symbol_spread", "arbitrage_opportunities", ["symbol", "spread_percent"])

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("opportunity_key", sa.String(length=180), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("buy_exchange", sa.String(length=50), nullable=False),
        sa.Column("sell_exchange", sa.String(length=50), nullable=False),
        sa.Column("spread_percent", sa.Numeric(12, 6), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False),
    )
    op.create_index("ix_notification_logs_key_sent_at", "notification_logs", ["opportunity_key", "sent_at"])

    op.create_table(
        "exchange_statuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("status", exchange_health, nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True)),
        sa.Column("last_error_at", sa.DateTime(timezone=True)),
        sa.Column("last_error_message", sa.Text()),
    )
    op.create_index("ix_exchange_statuses_exchange_name", "exchange_statuses", ["exchange_name"])

    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_name", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("market_type", market_type, nullable=False),
        sa.Column("bid_price", sa.Numeric(30, 12)),
        sa.Column("ask_price", sa.Numeric(30, 12)),
        sa.Column("last_price", sa.Numeric(30, 12), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_price_snapshots_symbol_timestamp", "price_snapshots", ["symbol", "timestamp"])
    op.create_index("ix_price_snapshots_exchange_symbol", "price_snapshots", ["exchange_name", "symbol"])

    exchanges = sa.table(
        "exchanges",
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
        sa.column("exchange_type", exchange_type),
    )
    op.bulk_insert(
        exchanges,
        [
            {"name": "Binance", "slug": "binance", "exchange_type": "CEX"},
            {"name": "Bybit", "slug": "bybit", "exchange_type": "CEX"},
            {"name": "MEXC", "slug": "mexc", "exchange_type": "CEX"},
            {"name": "Hyperliquid", "slug": "hyperliquid", "exchange_type": "PERP_DEX"},
        ],
    )

    pairs = sa.table(
        "trading_pairs",
        sa.column("symbol", sa.String),
        sa.column("base_asset", sa.String),
        sa.column("quote_asset", sa.String),
        sa.column("market_type", market_type),
    )
    op.bulk_insert(
        pairs,
        [
            {"symbol": f"{asset}/USDT", "base_asset": asset, "quote_asset": "USDT", "market_type": "PERPETUAL"}
            for asset in ("BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "TON")
        ],
    )


def downgrade() -> None:
    op.drop_table("price_snapshots")
    op.drop_table("exchange_statuses")
    op.drop_table("notification_logs")
    op.drop_table("arbitrage_opportunities")
    op.drop_table("app_settings")
    op.drop_table("trading_pairs")
    op.drop_table("exchanges")
    exchange_health.drop(op.get_bind(), checkfirst=True)
    opportunity_status.drop(op.get_bind(), checkfirst=True)
    market_type.drop(op.get_bind(), checkfirst=True)
    exchange_type.drop(op.get_bind(), checkfirst=True)
