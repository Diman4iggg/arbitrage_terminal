"""Arbitrage opportunity detection strategies."""

from app.strategies.base import Strategy
from app.strategies.price_spread import PriceSpreadStrategy

__all__ = ["PriceSpreadStrategy", "Strategy"]

