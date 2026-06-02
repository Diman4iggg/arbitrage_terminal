"""Add additional perpetual exchanges and optional popular pairs.

Revision ID: 20260603_0005
Revises: 20260602_0004
Create Date: 2026-06-03
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260603_0005"
down_revision: str | None = "20260602_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    exchange_type = sa.Enum("CEX", "PERP_DEX", name="exchange_type")
    exchanges = sa.table(
        "exchanges",
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
        sa.column("exchange_type", exchange_type),
    )
    op.bulk_insert(
        exchanges,
        [
            {"name": "Aster", "slug": "aster", "exchange_type": "PERP_DEX"},
            {
                "name": "Variational Omni",
                "slug": "variational-omni",
                "exchange_type": "PERP_DEX",
            },
            {"name": "BingX", "slug": "bingx", "exchange_type": "CEX"},
            {"name": "Bitget", "slug": "bitget", "exchange_type": "CEX"},
            {"name": "OKX", "slug": "okx", "exchange_type": "CEX"},
            {"name": "Gate.io", "slug": "gateio", "exchange_type": "CEX"},
        ],
    )

    market_type = sa.Enum("SPOT", "FUTURES", "PERPETUAL", name="market_type")
    pairs = sa.table(
        "trading_pairs",
        sa.column("symbol", sa.String),
        sa.column("base_asset", sa.String),
        sa.column("quote_asset", sa.String),
        sa.column("market_type", market_type),
        sa.column("enabled", sa.Boolean),
    )
    op.bulk_insert(
        pairs,
        [
            {
                "symbol": f"{asset}/USDT",
                "base_asset": asset,
                "quote_asset": "USDT",
                "market_type": "PERPETUAL",
                "enabled": False,
            }
            for asset in (
                "ADA",
                "AVAX",
                "LINK",
                "DOT",
                "LTC",
                "BCH",
                "TRX",
                "SUI",
                "APT",
                "ARB",
                "OP",
                "NEAR",
                "FIL",
                "PEPE",
                "WIF",
            )
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM trading_pairs WHERE symbol IN "
        "('ADA/USDT', 'AVAX/USDT', 'LINK/USDT', 'DOT/USDT', 'LTC/USDT', "
        "'BCH/USDT', 'TRX/USDT', 'SUI/USDT', 'APT/USDT', 'ARB/USDT', "
        "'OP/USDT', 'NEAR/USDT', 'FIL/USDT', 'PEPE/USDT', 'WIF/USDT')"
    )
    op.execute(
        "DELETE FROM exchanges WHERE slug IN "
        "('aster', 'variational-omni', 'bingx', 'bitget', 'okx', 'gateio')"
    )
