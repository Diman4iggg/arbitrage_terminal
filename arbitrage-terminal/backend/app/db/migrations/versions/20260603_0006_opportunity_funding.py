"""Add funding context to arbitrage opportunities.

Revision ID: 20260603_0006
Revises: 20260603_0005
Create Date: 2026-06-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260603_0006"
down_revision: str | None = "20260603_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("arbitrage_opportunities", sa.Column("buy_funding_rate_percent", sa.Numeric(12, 6)))
    op.add_column("arbitrage_opportunities", sa.Column("sell_funding_rate_percent", sa.Numeric(12, 6)))
    op.add_column("arbitrage_opportunities", sa.Column("funding_spread_percent", sa.Numeric(12, 6)))


def downgrade() -> None:
    op.drop_column("arbitrage_opportunities", "funding_spread_percent")
    op.drop_column("arbitrage_opportunities", "sell_funding_rate_percent")
    op.drop_column("arbitrage_opportunities", "buy_funding_rate_percent")
