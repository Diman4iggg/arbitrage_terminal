from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.scheduler import scheduler
from app.db.database import get_db_session
from app.db.models import ArbitrageOpportunity, Exchange, OpportunityStatus, TradingPair
from app.schemas.dashboard import DashboardRead, MonitoringStatus
from app.schemas.opportunity import OpportunityRead
from app.services.monitoring_state import monitoring_state

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardRead)
async def get_dashboard(session: AsyncSession = Depends(get_db_session)) -> DashboardRead:
    active_exchanges = await session.scalar(
        select(func.count()).select_from(Exchange).where(Exchange.enabled.is_(True))
    )
    tracked_pairs = await session.scalar(
        select(func.count()).select_from(TradingPair).where(TradingPair.enabled.is_(True))
    )
    current_opportunities = await session.scalar(
        select(func.count())
        .select_from(ArbitrageOpportunity)
        .where(ArbitrageOpportunity.status == OpportunityStatus.ACTIVE)
    )
    max_spread = await session.scalar(
        select(func.max(ArbitrageOpportunity.spread_percent)).where(
            ArbitrageOpportunity.status == OpportunityStatus.ACTIVE
        )
    )
    recent_result = await session.execute(
        select(ArbitrageOpportunity)
        .order_by(ArbitrageOpportunity.detected_at.desc())
        .limit(10)
    )
    return DashboardRead(
        active_exchanges=active_exchanges or 0,
        tracked_pairs=tracked_pairs or 0,
        current_opportunities=current_opportunities or 0,
        max_spread_percent=Decimal(max_spread) if max_spread is not None else None,
        monitoring=MonitoringStatus(
            scheduler_enabled=settings.scheduler_enabled,
            scheduler_running=scheduler.running,
            cycle_running=monitoring_state.running,
            last_started_at=monitoring_state.last_started_at,
            last_completed_at=monitoring_state.last_completed_at,
            last_error=monitoring_state.last_error,
            cycle_errors=monitoring_state.errors,
        ),
        recent_opportunities=[
            OpportunityRead.model_validate(item) for item in recent_result.scalars()
        ],
    )
