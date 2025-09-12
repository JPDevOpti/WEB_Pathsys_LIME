import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.core.exceptions import (
    ConflictError,
    BadRequestError,
    NotFoundError
)
from app.modules.facturacion.repositories.facturacion_repository import FacturacionRepository
from app.modules.facturacion.services.facturacion_service import FacturacionService
from app.modules.facturacion.schemas.facturacion import (
    FacturacionCreate,
    FacturacionUpdate,
    FacturacionResponse,
    FacturacionSearch,
    FacturacionEstadoUpdate
)
from app.shared.services.user_management import UserManagementService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["facturacion"])

def get_facturacion_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> FacturacionService:
    facturacion_repository = FacturacionRepository(db)
    user_management_service = UserManagementService(db)
    return FacturacionService(facturacion_repository, user_management_service)

@router.post("/", response_model=FacturacionResponse, status_code=201)
async def create_facturacion(
    facturacion_data: FacturacionCreate,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Crear un nuevo usuario de facturación"""
    try:
        logger.info(f"Creando usuario de facturación: {facturacion_data.facturacion_email}")
        return await service.create_facturacion(facturacion_data)
    except ConflictError as e:
        logger.warning(f"Conflicto al crear usuario de facturación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Datos inválidos al crear usuario de facturación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al crear usuario de facturación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/", response_model=List[FacturacionResponse])
async def get_facturacion_list(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Obtener lista de usuarios de facturación activos con paginación"""
    try:
        return await service.get_facturacion_list(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_facturacion(
    query: str = Query(None, description="Término de búsqueda general"),
    facturacion_name: str = Query(None, description="Nombre del usuario de facturación"),
    facturacion_code: str = Query(None, description="Código del usuario de facturación"),
    facturacion_email: str = Query(None, description="Email del usuario de facturación"),
    is_active: bool = Query(None, description="Estado del usuario de facturación"),
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Buscar usuarios de facturación con filtros avanzados"""
    try:
        if query:
            search_params = FacturacionSearch(
                facturacion_name=query,
                facturacion_code=query,
                facturacion_email=query,
                is_active=is_active
            )
        else:
            search_params = FacturacionSearch(
                facturacion_name=facturacion_name,
                facturacion_code=facturacion_code,
                facturacion_email=facturacion_email,
                is_active=is_active
            )
        
        facturacion_list = await service.search_facturacion(search_params)
        
        return {
            "facturacion": facturacion_list,
            "total": len(facturacion_list),
            "filtros_aplicados": {
                "facturacion_name": facturacion_name,
                "facturacion_code": facturacion_code,
                "facturacion_email": facturacion_email,
                "is_active": is_active
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/search/active", response_model=Dict[str, Any])
async def search_active_facturacion(
    query: str = Query(None, description="Término de búsqueda general"),
    facturacion_name: str = Query(None, description="Nombre del usuario de facturación"),
    facturacion_code: str = Query(None, description="Código del usuario de facturación"),
    facturacion_email: str = Query(None, description="Email del usuario de facturación"),
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Buscar solo usuarios de facturación activos con filtros avanzados"""
    try:
        if query:
            search_params = FacturacionSearch(
                facturacion_name=query,
                facturacion_code=query,
                facturacion_email=query
            )
        else:
            search_params = FacturacionSearch(
                facturacion_name=facturacion_name,
                facturacion_code=facturacion_code,
                facturacion_email=facturacion_email
            )
        
        facturacion_list = await service.search_active_facturacion(search_params)
        
        return {
            "facturacion": facturacion_list,
            "total": len(facturacion_list),
            "filtros_aplicados": {
                "facturacion_name": facturacion_name,
                "facturacion_code": facturacion_code,
                "facturacion_email": facturacion_email,
                "is_active": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/search/all-including-inactive", response_model=Dict[str, Any])
async def search_all_facturacion_including_inactive(
    query: str = Query(None, description="Término de búsqueda general"),
    facturacion_name: str = Query(None, description="Nombre del usuario de facturación"),
    facturacion_code: str = Query(None, description="Código del usuario de facturación"),
    facturacion_email: str = Query(None, description="Email del usuario de facturación"),
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Buscar todos los usuarios de facturación incluyendo inactivos con filtros avanzados"""
    try:
        if query:
            search_params = FacturacionSearch(
                facturacion_name=query,
                facturacion_code=query,
                facturacion_email=query
            )
        else:
            search_params = FacturacionSearch(
                facturacion_name=facturacion_name,
                facturacion_code=facturacion_code,
                facturacion_email=facturacion_email
            )
        
        facturacion_list = await service.search_all_facturacion_including_inactive(search_params)
        
        return {
            "facturacion": facturacion_list,
            "total": len(facturacion_list),
            "filtros_aplicados": {
                "facturacion_name": facturacion_name,
                "facturacion_code": facturacion_code,
                "facturacion_email": facturacion_email,
                "is_active": "all"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/activos", response_model=List[FacturacionResponse])
async def get_facturacion_activos(
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Obtener todos los usuarios de facturación activos"""
    try:
        return await service.get_facturacion_activos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/inactivos", response_model=List[FacturacionResponse])
async def get_facturacion_inactivos(
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Obtener todos los usuarios de facturación inactivos"""
    try:
        return await service.get_facturacion_inactivos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/estadisticas", response_model=Dict[str, Any])
async def get_estadisticas_facturacion(
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Obtener estadísticas de usuarios de facturación"""
    try:
        return await service.get_estadisticas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{facturacion_code}", response_model=FacturacionResponse)
async def get_facturacion(
    facturacion_code: str,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Obtener un usuario de facturación por código"""
    try:
        return await service.get_facturacion(facturacion_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{facturacion_code}", response_model=FacturacionResponse)
async def update_facturacion(
    facturacion_code: str,
    facturacion_data: FacturacionUpdate,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Actualizar un usuario de facturación"""
    try:
        return await service.update_facturacion(facturacion_code, facturacion_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{facturacion_code}", status_code=200)
async def delete_facturacion(
    facturacion_code: str,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Eliminar permanentemente un usuario de facturación de la base de datos"""
    try:
        success = await service.delete_facturacion(facturacion_code)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario de facturación")
        return {"message": f"Usuario de facturación con código {facturacion_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{facturacion_code}/activar", response_model=FacturacionResponse)
async def activate_facturacion(
    facturacion_code: str,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Activar un usuario de facturación"""
    try:
        return await service.activate_facturacion(facturacion_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{facturacion_code}/estado", response_model=FacturacionResponse)
async def update_facturacion_estado(
    facturacion_code: str,
    estado_data: FacturacionEstadoUpdate,
    service: FacturacionService = Depends(get_facturacion_service)
):
    """Actualizar solo el estado de un usuario de facturación"""
    try:
        facturacion_update = FacturacionUpdate(
            facturacion_name=None,
            facturacion_code=None,
            facturacion_email=None,
            observaciones=None,
            is_active=estado_data.is_active
        )
        return await service.update_facturacion(facturacion_code, facturacion_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
