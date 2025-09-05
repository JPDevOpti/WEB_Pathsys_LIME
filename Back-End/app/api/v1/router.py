from fastapi import APIRouter
from app.config.settings import settings
from app.modules.auth.routes.auth_routes import auth_router
from app.modules.pacientes.routes.paciente_routes import router as pacientes_router
from app.modules.casos.routes.caso_routes import router as casos_router
from app.modules.casos.routes.consecutivo_routes import router as consecutivos_router
from app.modules.pruebas.routes.prueba_routes import router as pruebas_router
from app.modules.entidades.routes.entidad_routes import router as entidades_router
from app.modules.patologos.routes.patologo_routes import router as patologos_router
from app.modules.residentes.routes.residente_routes import router as residentes_router
from app.modules.auxiliares.routes import auxiliares_router
from app.modules.enfermedades.routes import router as enfermedad_router
from app.modules.aprobacion.routes.caso_aprobacion_routes import router as aprobacion_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["autenticación"])
api_router.include_router(pacientes_router, prefix="/pacientes", tags=["pacientes"])
api_router.include_router(casos_router, prefix="/casos", tags=["casos"])
api_router.include_router(consecutivos_router, prefix="/consecutivos", tags=["consecutivos"])
api_router.include_router(pruebas_router, prefix="/pruebas", tags=["pruebas"])
api_router.include_router(entidades_router, prefix="/entidades", tags=["entidades"])
api_router.include_router(patologos_router, prefix="/patologos", tags=["patologos"])
api_router.include_router(residentes_router, prefix="/residentes", tags=["residentes"])
api_router.include_router(auxiliares_router, prefix="/auxiliares", tags=["auxiliares"])
api_router.include_router(enfermedad_router, prefix="/enfermedades", tags=["enfermedades"])
api_router.include_router(aprobacion_router, prefix="/aprobacion", tags=["aprobacion"])

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
        "modules_implementados": [
            "autenticación",
            "casos", 
            "pacientes",
            "pruebas",
            "entidades",
            "patologos",
            "residentes",
            "auxiliares",
            "enfermedades",
            "aprobación"
        ],
        "modules_pendientes": [
            "estadisticas",
            "resultados",
            "notificaciones"
        ]
    }