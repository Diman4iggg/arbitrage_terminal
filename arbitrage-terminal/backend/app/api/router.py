from fastapi import APIRouter

from app.api.routes.charts import router as charts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.exchanges import router as exchanges_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.pairs import router as pairs_router
from app.api.routes.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(exchanges_router)
api_router.include_router(pairs_router)
api_router.include_router(opportunities_router)
api_router.include_router(settings_router)
api_router.include_router(charts_router)
api_router.include_router(notifications_router)
