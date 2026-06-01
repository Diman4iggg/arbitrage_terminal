from dataclasses import dataclass, field
from datetime import datetime

from app.schemas.opportunity import Opportunity
from app.schemas.ticker import Ticker


@dataclass(slots=True)
class MonitoringState:
    running: bool = False
    last_started_at: datetime | None = None
    last_completed_at: datetime | None = None
    last_error: str | None = None
    tickers: list[Ticker] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)


monitoring_state = MonitoringState()
