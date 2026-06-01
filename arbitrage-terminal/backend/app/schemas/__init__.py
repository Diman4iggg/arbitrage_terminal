"""Normalized domain and API schemas."""

from app.schemas.chart import PriceChartRead, PricePoint, SpreadChartRead, SpreadPoint, TopSpreadPoint
from app.schemas.dashboard import DashboardRead, MonitoringStatus
from app.schemas.exchange import ExchangeRead, ExchangeStatusRead, ExchangeUpdate, ExchangeWithStatusRead
from app.schemas.notification import NotificationTestResult
from app.schemas.opportunity import Opportunity, OpportunityRead
from app.schemas.pair import TradingPairRead, TradingPairUpdate
from app.schemas.settings import RuntimeSettings, RuntimeSettingsUpdate
from app.schemas.ticker import FundingRate, Market, Ticker

__all__ = [
    "ExchangeRead",
    "ExchangeStatusRead",
    "ExchangeUpdate",
    "ExchangeWithStatusRead",
    "FundingRate",
    "Market",
    "Opportunity",
    "OpportunityRead",
    "DashboardRead",
    "MonitoringStatus",
    "NotificationTestResult",
    "PriceChartRead",
    "PricePoint",
    "RuntimeSettings",
    "RuntimeSettingsUpdate",
    "SpreadChartRead",
    "SpreadPoint",
    "Ticker",
    "TradingPairRead",
    "TradingPairUpdate",
    "TopSpreadPoint",
]
