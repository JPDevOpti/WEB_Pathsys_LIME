from fastapi import APIRouter
from app.config.settings import settings
from app.modules.auth.routes.auth_routes import auth_router
from app.modules.patients.routes import router as patients_router
from app.modules.entities.routes import router as entities_router
from app.modules.tests.routes import router as tests_router
from app.modules.cases import router as cases_router
from app.modules.pathologists.routes import router as pathologists_router
from app.modules.residents.routes import router as residents_router
from app.modules.auxiliaries.routes import router as auxiliaries_router
from app.modules.billing.routes import router as billing_router
from app.modules.diseases.routes.disease_routes import router as diseases_router
from app.modules.tickets.routes import router as tickets_router
from app.modules.approvals.routes import approval_router as approvals_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(patients_router, prefix="/patients", tags=["patients"])
api_router.include_router(entities_router, prefix="/entities", tags=["entities"])
api_router.include_router(tests_router, prefix="/tests", tags=["tests"])
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])
api_router.include_router(pathologists_router, prefix="/pathologists", tags=["pathologists"])
api_router.include_router(residents_router, prefix="/residents", tags=["residents"])
api_router.include_router(auxiliaries_router, prefix="/auxiliaries", tags=["auxiliaries"])
api_router.include_router(billing_router, prefix="/billing", tags=["billing"])
api_router.include_router(diseases_router, prefix="/diseases", tags=["diseases"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(approvals_router, prefix="/approvals", tags=["approvals"])

@api_router.get("/health")
async def health_check():
    """Endpoint de verificación de salud de la API"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "message": f"{settings.PROJECT_NAME} está funcionando correctamente"
    }

@api_router.get("/info")
async def api_info():
    """Información de la API"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "modules_implemented": [
            "auth",
            "patients",
            "entities",
            "tests",
            "cases",
            "pathologists",
            "residents",
            "auxiliaries",
            "billing",
            "diseases",
            "tickets",
            "approvals",
        ],
        "modules_pending": []
    }