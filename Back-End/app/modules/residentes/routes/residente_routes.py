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
from app.modules.residentes.repositories.residente_repository import ResidenteRepository
from app.modules.residentes.services.residente_service import ResidenteService
from app.modules.residentes.schemas.residente import (
    ResidenteCreate,
    ResidenteUpdate,
    ResidenteResponse,
    ResidenteSearch,
    ResidenteEstadoUpdate
)
from app.shared.services.user_management import UserManagementService

router = APIRouter(tags=["residentes"])
logger = logging.getLogger(__name__)

# Dependency para obtener el servicio
def get_residente_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ResidenteService:
    residente_repository = ResidenteRepository(db)
    user_management_service = UserManagementService(db)
    return ResidenteService(residente_repository, user_management_service)

@router.post("/", response_model=ResidenteResponse, status_code=201)
async def create_residente(
    residente_data: ResidenteCreate,
    service: ResidenteService = Depends(get_residente_service)
):
    """Crear un nuevo residente"""
    try:
        logger.info(f"Creando nuevo residente: {residente_data.residente_code}")
        return await service.create_residente(residente_data)
    except ConflictError as e:
        logger.warning(f"Conflicto al crear residente: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Datos inválidos al crear residente: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado creando residente: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[ResidenteResponse])
async def get_residentes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: ResidenteService = Depends(get_residente_service)
):
    """Obtener lista de residentes activos con paginación"""
    try:
        logger.info(f"Obteniendo residentes - skip: {skip}, limit: {limit}")
        return await service.get_residentes(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado obteniendo residentes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/search", response_model=Dict[str, Any])
async def search_residentes(
    residente_name: str = Query(None, description="Nombre del residente"),
    iniciales_residente: str = Query(None, description="Iniciales del residente"),
    residente_code: str = Query(None, description="Código del residente"),
    residente_email: str = Query(None, description="Email del residente"),
    registro_medico: str = Query(None, description="Registro médico"),
    is_active: bool = Query(None, description="Estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: ResidenteService = Depends(get_residente_service)
):
    """Búsqueda avanzada de residentes"""
    try:
        search_params = ResidenteSearch(
            residente_name=residente_name,
            iniciales_residente=iniciales_residente,
            residente_code=residente_code,
            residente_email=residente_email,
            registro_medico=registro_medico,
            is_active=is_active
        )
        logger.info(f"Buscando residentes - skip: {skip}, limit: {limit}")
        return await service.search_residentes(search_params, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado buscando residentes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{residente_code}", response_model=ResidenteResponse)
async def get_residente(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Obtener un residente por código"""
    try:
        logger.info(f"Buscando residente por código: {residente_code}")
        return await service.get_residente(residente_code)
    except NotFoundError as e:
        logger.warning(f"Residente no encontrado: {residente_code}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado obteniendo residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{residente_code}", response_model=ResidenteResponse)
async def update_residente(
    residente_code: str,
    residente_data: ResidenteUpdate,
    service: ResidenteService = Depends(get_residente_service)
):
    """Actualizar un residente por código"""
    try:
        logger.info(f"Actualizando residente: {residente_code}")
        return await service.update_residente(residente_code, residente_data)
    except NotFoundError as e:
        logger.warning(f"Residente no encontrado para actualizar: {residente_code}")
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflicto al actualizar residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Datos inválidos al actualizar residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado actualizando residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{residente_code}", status_code=200)
async def delete_residente(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Eliminar (soft delete) un residente por código"""
    try:
        logger.info(f"Eliminando residente: {residente_code}")
        await service.delete_residente(residente_code)
        return {"message": f"Residente con código {residente_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        logger.warning(f"Residente no encontrado para eliminar: {residente_code}")
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al eliminar residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado eliminando residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.patch("/{residente_code}/toggle-estado", response_model=ResidenteResponse)
async def toggle_estado(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Cambiar el estado activo/inactivo de un residente"""
    try:
        logger.info(f"Cambiando estado de residente: {residente_code}")
        return await service.toggle_estado(residente_code)
    except NotFoundError as e:
        logger.warning(f"Residente no encontrado para cambiar estado: {residente_code}")
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al cambiar estado de residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado cambiando estado de residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{residente_code}/estado", response_model=ResidenteResponse)
async def cambiar_estado(
    residente_code: str,
    estado_data: ResidenteEstadoUpdate,
    service: ResidenteService = Depends(get_residente_service)
):
    """Cambiar el estado de un residente (PUT endpoint)"""
    try:
        logger.info(f"Cambiando estado de residente: {residente_code} a {estado_data.is_active}")
        # Obtener el residente actual
        residente_response = await service.get_residente(residente_code)
        
        # Crear ResidenteUpdate con el nuevo estado
        residente_update = ResidenteUpdate(
            residente_name=residente_response.residente_name,
            iniciales_residente=residente_response.iniciales_residente,
            residente_code=residente_response.residente_code,
            residente_email=residente_response.residente_email,
            registro_medico=residente_response.registro_medico,
            observaciones=residente_response.observaciones,
            is_active=estado_data.is_active
        )
        
        return await service.update_residente(residente_code, residente_update)
    except NotFoundError as e:
        logger.warning(f"Residente no encontrado para cambiar estado: {residente_code}")
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al cambiar estado de residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado cambiando estado de residente {residente_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")