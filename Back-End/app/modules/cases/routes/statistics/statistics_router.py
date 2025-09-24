# Main Statistics Router
from fastapi import APIRouter

# Import individual statistics routers
from .dashboard_statistics_routes import router as dashboard_router
from .opportunity_statistics_routes import router as opportunity_router
from .pathologist_statistics_routes import router as pathologist_router
from .entity_statistics_routes import router as entity_router
from .test_statistics_routes import router as test_router

router = APIRouter(prefix="/statistics", tags=["statistics"])

# Include individual statistics routers
router.include_router(dashboard_router)
router.include_router(opportunity_router)
router.include_router(pathologist_router)
router.include_router(entity_router, prefix="/entities")
router.include_router(test_router, prefix="/tests")
