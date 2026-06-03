"""Add directional alert conditions to trade watches.

Revision ID: 20260603_0007
Revises: 20260603_0006
Create Date: 2026-06-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260603_0007"
down_revision: str | None = "20260603_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "trade_watches",
        sa.Column("price_alert_condition", sa.String(length=10), server_default="above", nullable=False),
    )
    op.add_column(
        "trade_watches",
        sa.Column("funding_alert_condition", sa.String(length=10), server_default="above", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("trade_watches", "funding_alert_condition")
    op.drop_column("trade_watches", "price_alert_condition")
