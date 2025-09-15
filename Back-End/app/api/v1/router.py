from fastapi import APIRouter
from app.config.settings import settings
from app.modules.auth.routes.auth_routes import auth_router
from app.modules.pacientes.routes.paciente_routes import router as pacientes_router
from app.modules.casos.routes.caso_routes import router as casos_router
from app.modules.casos.routes.stats_routes import router as casos_stats_router
from app.modules.casos.routes.management_routes import router as casos_management_router
from app.modules.casos.routes.management.create_routes import router as casos_management_create_router
from app.modules.casos.routes.management.update_routes import router as casos_management_update_router
from app.modules.casos.routes.query.case_list_routes import router as casos_query_case_list_router
from app.modules.casos.routes.query.urgent_cases_routes import router as casos_query_urgent_router
from app.modules.casos.routes.query.pathologist_cases_routes import router as casos_query_pathologist_router
from app.modules.casos.routes.query.entity_cases_routes import router as casos_query_entity_router
from app.modules.casos.routes.query.delivery_queue_routes import router as casos_query_queue_router
from app.modules.casos.routes.query.search_routes import router as casos_query_search_router
from app.modules.casos.routes.consecutivo_routes import router as consecutivos_router
from app.modules.pruebas.routes.prueba_routes import router as pruebas_router
from app.modules.entidades.routes.entidad_routes import router as entidades_router
from app.modules.patologos.routes.patologo_routes import router as patologos_router
from app.modules.residentes.routes.residente_routes import router as residentes_router
from app.modules.auxiliares.routes import auxiliares_router
from app.modules.facturacion.routes import facturacion_router
from app.modules.enfermedades.routes import router as enfermedad_router
from app.modules.aprobacion.routes.caso_aprobacion_routes import router as aprobacion_router
from app.modules.tickets.routes.ticket_routes import router as tickets_router
from app.modules.dashboard.routes.dashboard_routes import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["autenticación"])
api_router.include_router(pacientes_router, prefix="/pacientes", tags=["pacientes"])
api_router.include_router(casos_router, prefix="/casos", tags=["casos"])
api_router.include_router(casos_stats_router, prefix="/casos", tags=["casos"])  # estadísticas de casos
api_router.include_router(casos_management_router, prefix="/casos", tags=["casos"])  # gestión (vacío)
api_router.include_router(casos_management_create_router, prefix="/casos", tags=["casos-management-create"])  # creación optimizada
api_router.include_router(casos_management_update_router, prefix="/casos", tags=["casos-management-update"])  # actualización optimizada
api_router.include_router(casos_query_case_list_router, prefix="/casos", tags=["casos"])  # consulta/listado (vacío)
api_router.include_router(casos_query_urgent_router, prefix="/casos", tags=["casos"])  # consulta urgentes (vacío)
api_router.include_router(casos_query_pathologist_router, prefix="/casos", tags=["casos"])  # consulta por patólogo (vacío)
api_router.include_router(casos_query_entity_router, prefix="/casos", tags=["casos"])  # consulta por entidad (vacío)
api_router.include_router(casos_query_queue_router, prefix="/casos", tags=["casos"])  # colas (vacío)
api_router.include_router(casos_query_search_router, prefix="/casos", tags=["casos"])  # búsqueda (vacío)
api_router.include_router(consecutivos_router, prefix="/consecutivos", tags=["consecutivos"])
api_router.include_router(pruebas_router, prefix="/pruebas", tags=["pruebas"])
api_router.include_router(entidades_router, prefix="/entidades", tags=["entidades"])
api_router.include_router(patologos_router, prefix="/patologos", tags=["patologos"])
api_router.include_router(residentes_router, prefix="/residentes", tags=["residentes"])
api_router.include_router(auxiliares_router, prefix="/auxiliares", tags=["auxiliares"])
api_router.include_router(facturacion_router, prefix="/facturacion", tags=["facturacion"])
api_router.include_router(enfermedad_router, prefix="/enfermedades", tags=["enfermedades"])
api_router.include_router(aprobacion_router, prefix="/aprobacion", tags=["aprobacion"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

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
            "facturacion",
            "enfermedades",
            "aprobación",
            "tickets",
            "dashboard"
        ],
        "modules_pendientes": [
            "resultados",
            "notificaciones"
        ]
    }