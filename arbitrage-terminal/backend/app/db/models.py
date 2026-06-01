from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, Index, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExchangeType(StrEnum):
    CEX = "cex"
    PERP_DEX = "perp_dex"


class MarketType(StrEnum):
    SPOT = "spot"
    FUTURES = "futures"
    PERPETUAL = "perpetual"


class OpportunityStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


class ExchangeHealth(StrEnum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Exchange(TimestampMixin, Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    exchange_type: Mapped[ExchangeType] = mapped_column(
        Enum(ExchangeType, name="exchange_type"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)


class TradingPair(TimestampMixin, Base):
    __tablename__ = "trading_pairs"
    __table_args__ = (
        Index("ix_trading_pairs_symbol_market_type", "symbol", "market_type", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    base_asset: Mapped[str] = mapped_column(String(30), nullable=False)
    quote_asset: Mapped[str] = mapped_column(String(30), nullable=False)
    market_type: Mapped[MarketType] = mapped_column(
        Enum(MarketType, name="market_type"), default=MarketType.PERPETUAL, nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)


class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"
    __table_args__ = (
        Index("ix_opportunities_detected_at", "detected_at"),
        Index("ix_opportunities_symbol_spread", "symbol", "spread_percent"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    market_type: Mapped[MarketType] = mapped_column(Enum(MarketType, name="market_type"), nullable=False)
    buy_exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    sell_exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(30, 12), nullable=False)
    sell_price: Mapped[Decimal] = mapped_column(Numeric(30, 12), nullable=False)
    spread_percent: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status"),
        default=OpportunityStatus.ACTIVE,
        nullable=False,
    )


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    __table_args__ = (Index("ix_notification_logs_key_sent_at", "opportunity_key", "sent_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_key: Mapped[str] = mapped_column(String(180), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    buy_exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    sell_exchange: Mapped[str] = mapped_column(String(50), nullable=False)
    spread_percent: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)


class ExchangeStatus(Base):
    __tablename__ = "exchange_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    status: Mapped[ExchangeHealth] = mapped_column(
        Enum(ExchangeHealth, name="exchange_health"),
        default=ExchangeHealth.UNKNOWN,
        nullable=False,
    )
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_message: Mapped[str | None] = mapped_column(Text)


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (
        Index("ix_price_snapshots_symbol_timestamp", "symbol", "timestamp"),
        Index("ix_price_snapshots_exchange_symbol", "exchange_name", "symbol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    market_type: Mapped[MarketType] = mapped_column(Enum(MarketType, name="market_type"), nullable=False)
    bid_price: Mapped[Decimal | None] = mapped_column(Numeric(30, 12))
    ask_price: Mapped[Decimal | None] = mapped_column(Numeric(30, 12))
    last_price: Mapped[Decimal] = mapped_column(Numeric(30, 12), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

