"""Add entry prices, position size and live PnL to trade watches.

Revision ID: 20260602_0003
Revises: 20260602_0002
Create Date: 2026-06-02
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260602_0003"
down_revision: str | None = "20260602_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("trade_watches", sa.Column("buy_entry_price", sa.Numeric(30, 12)))
    op.add_column("trade_watches", sa.Column("sell_entry_price", sa.Numeric(30, 12)))
    op.add_column("trade_watches", sa.Column("position_size_coins", sa.Numeric(30, 12)))
    op.add_column("trade_watches", sa.Column("pnl_usdt", sa.Numeric(30, 12)))
    op.add_column("trade_watches", sa.Column("pnl_percent", sa.Numeric(12, 6)))


def downgrade() -> None:
    op.drop_column("trade_watches", "pnl_percent")
    op.drop_column("trade_watches", "pnl_usdt")
    op.drop_column("trade_watches", "position_size_coins")
    op.drop_column("trade_watches", "sell_entry_price")
    op.drop_column("trade_watches", "buy_entry_price")
