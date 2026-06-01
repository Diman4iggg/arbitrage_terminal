"""Normalized domain and API schemas."""

from app.schemas.exchange import ExchangeRead, ExchangeStatusRead, ExchangeUpdate
from app.schemas.opportunity import Opportunity, OpportunityRead
from app.schemas.pair import TradingPairRead, TradingPairUpdate
from app.schemas.settings import RuntimeSettings, RuntimeSettingsUpdate
from app.schemas.ticker import FundingRate, Market, Ticker

__all__ = [
    "ExchangeRead",
    "ExchangeStatusRead",
    "ExchangeUpdate",
    "FundingRate",
    "Market",
    "Opportunity",
    "OpportunityRead",
    "RuntimeSettings",
    "RuntimeSettingsUpdate",
    "Ticker",
    "TradingPairRead",
    "TradingPairUpdate",
]
