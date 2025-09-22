# Main Statistics Router
from fastapi import APIRouter

# TODO: Import individual statistics routers when implemented
# from .dashboard_statistics_routes import router as dashboard_router
# from .opportunity_statistics_routes import router as opportunity_router
# from .pathologist_statistics_routes import router as pathologist_router
# from .entity_statistics_routes import router as entity_router
# from .test_statistics_routes import router as test_router

router = APIRouter(prefix="/statistics", tags=["statistics"])

# TODO: Include individual statistics routers when implemented
# router.include_router(dashboard_router, prefix="/dashboard")
# router.include_router(opportunity_router, prefix="/opportunity")
# router.include_router(pathologist_router, prefix="/pathologist")
# router.include_router(entity_router, prefix="/entity")
# router.include_router(test_router, prefix="/test")
