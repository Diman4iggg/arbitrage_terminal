from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.opportunity import OpportunityRead


class MonitoringStatus(BaseModel):
    scheduler_enabled: bool
    scheduler_running: bool
    cycle_running: bool
    last_started_at: datetime | None
    last_completed_at: datetime | None
    last_error: str | None
    cycle_errors: dict[str, str] = Field(default_factory=dict)


class DashboardRead(BaseModel):
    active_exchanges: int
    tracked_pairs: int
    current_opportunities: int
    max_spread_percent: Decimal | None
    monitoring: MonitoringStatus
    recent_opportunities: list[OpportunityRead]
