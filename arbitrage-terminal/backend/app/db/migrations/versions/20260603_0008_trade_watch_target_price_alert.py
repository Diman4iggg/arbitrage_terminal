"""Add target price alert rule to trade watches.

Revision ID: 20260603_0008
Revises: 20260603_0007
Create Date: 2026-06-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260603_0008"
down_revision: str | None = "20260603_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("trade_watches", sa.Column("target_price_alert_value", sa.Numeric(30, 12)))
    op.add_column(
        "trade_watches",
        sa.Column("target_price_alert_condition", sa.String(length=10), server_default="above", nullable=False),
    )
    op.add_column(
        "trade_watches",
        sa.Column("target_price_alert_source", sa.String(length=10), server_default="buy", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("trade_watches", "target_price_alert_source")
    op.drop_column("trade_watches", "target_price_alert_condition")
    op.drop_column("trade_watches", "target_price_alert_value")
