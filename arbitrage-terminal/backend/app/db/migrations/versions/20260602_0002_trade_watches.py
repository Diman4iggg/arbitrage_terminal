"""Add manually tracked trade watches.

Revision ID: 20260602_0002
Revises: 20260601_0001
Create Date: 2026-06-02
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0002"
down_revision: str | None = "20260601_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trade_watches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("buy_exchange", sa.String(length=50), nullable=False),
        sa.Column("sell_exchange", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("notifications_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("price_alert_threshold_percent", sa.Numeric(12, 6)),
        sa.Column("funding_alert_threshold_percent", sa.Numeric(12, 6)),
        sa.Column("buy_price", sa.Numeric(30, 12)),
        sa.Column("sell_price", sa.Numeric(30, 12)),
        sa.Column("price_spread_percent", sa.Numeric(12, 6)),
        sa.Column("buy_funding_rate_percent", sa.Numeric(12, 6)),
        sa.Column("sell_funding_rate_percent", sa.Numeric(12, 6)),
        sa.Column("funding_spread_percent", sa.Numeric(12, 6)),
        sa.Column("last_updated_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_trade_watches_symbol_exchanges",
        "trade_watches",
        ["symbol", "buy_exchange", "sell_exchange"],
    )


def downgrade() -> None:
    op.drop_table("trade_watches")
