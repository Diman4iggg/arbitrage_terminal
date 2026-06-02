"""Add spread history snapshots for manually tracked trades.

Revision ID: 20260602_0004
Revises: 20260602_0003
Create Date: 2026-06-02
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0004"
down_revision: str | None = "20260602_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trade_watch_spread_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "trade_watch_id",
            sa.Integer(),
            sa.ForeignKey("trade_watches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("spread_percent", sa.Numeric(12, 6), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_trade_watch_spread_snapshots_watch_timestamp",
        "trade_watch_spread_snapshots",
        ["trade_watch_id", "timestamp"],
    )


def downgrade() -> None:
    op.drop_table("trade_watch_spread_snapshots")
