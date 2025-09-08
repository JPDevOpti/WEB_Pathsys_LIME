"""Rutas de la API para el módulo de Patólogos"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from app.modules.patologos.services.patologo_service import PatologoService
from app.modules.patologos.schemas.patologo import (
    PatologoCreate,
    PatologoUpdate,
    PatologoResponse,
    PatologoSearch,
    PatologoEstadoUpdate,
    PatologoFirmaUpdate
)
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ConflictError
)
from app.config.database import get_database
from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.shared.services.user_management import UserManagementService

router = APIRouter(tags=["patologos"])
logger = logging.getLogger(__name__)

# Dependency para obtener el servicio de patólogos
async def get_patologo_service(database=Depends(get_database)) -> PatologoService:
    """Obtener instancia del servicio de patólogos"""
    patologo_repository = PatologoRepository(database)
    user_management_service = UserManagementService(database)
    return PatologoService(patologo_repository, user_management_service)

@router.post("/", response_model=PatologoResponse, status_code=status.HTTP_201_CREATED)
async def create_patologo(
    patologo: PatologoCreate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Crear un nuevo patólogo"""
    try:
        logger.info(f"Creando nuevo patólogo: {patologo.patologo_code}")
        return await patologo_service.create_patologo(patologo)
    except ConflictError as e:
        logger.warning(f"Conflicto al crear patólogo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Datos inválidos al crear patólogo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado creando patólogo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/", response_model=List[PatologoResponse])
async def get_patologos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Obtener lista de patólogos con paginación
    """
    try:
        logger.info(f"Obteniendo patólogos - skip: {skip}, limit: {limit}")
        return await patologo_service.get_patologos(skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado obteniendo patólogos: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@router.get("/search", response_model=List[PatologoResponse])
async def search_patologos(
    q: Optional[str] = Query(None, description="Término de búsqueda general (nombre, código, email, registro médico)"),
    is_active: Optional[bool] = Query(None, description="Estado del patólogo (activo/inactivo)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Búsqueda avanzada de patólogos
    """
    try:
        search_params = PatologoSearch(
            q=q,
            patologo_name=None,
            patologo_code=None,
            patologo_email=None,
            registro_medico=None,
            is_active=is_active,
            observaciones=None
        )
        logger.info(f"Buscando patólogos - skip: {skip}, limit: {limit}, is_active: {is_active}")
        return await patologo_service.search_patologos(search_params=search_params, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado buscando patólogos: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/search/active", response_model=List[PatologoResponse])
async def search_active_patologos(
    q: Optional[str] = Query(None, description="Término de búsqueda general (nombre, código, email, registro médico)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Búsqueda de solo patólogos activos
    """
    try:
        search_params = PatologoSearch(
            q=q,
            patologo_name=None,
            patologo_code=None,
            patologo_email=None,
            registro_medico=None,
            is_active=None,
            observaciones=None
        )
        logger.info(f"Buscando patólogos activos - skip: {skip}, limit: {limit}")
        return await patologo_service.search_active_patologos(search_params=search_params, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado buscando patólogos activos: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/search/all-including-inactive", response_model=List[PatologoResponse])
async def search_all_patologos_including_inactive(
    q: Optional[str] = Query(None, description="Término de búsqueda general (nombre, código, email, registro médico)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Búsqueda de todos los patólogos incluyendo inactivos
    """
    try:
        search_params = PatologoSearch(
            q=q,
            patologo_name=None,
            patologo_code=None,
            patologo_email=None,
            registro_medico=None,
            is_active=None,
            observaciones=None
        )
        logger.info(f"Buscando todos los patólogos incluyendo inactivos - skip: {skip}, limit: {limit}")
        return await patologo_service.search_all_patologos_including_inactive(search_params=search_params, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error inesperado buscando todos los patólogos: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")





@router.get("/{patologo_code}/info", response_model=Dict[str, Any])
async def get_patologo_info_for_assignment(
    patologo_code: str = Path(..., description="Código del patólogo"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Obtener información completa del patólogo incluyendo firma para asignación a casos
    """
    try:
        logger.info(f"Obteniendo información completa de patólogo: {patologo_code}")
        return await patologo_service.get_patologo_info_for_assignment(patologo_code)
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para info: {patologo_code}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado obteniendo info de patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/{identifier}", response_model=PatologoResponse)
async def get_patologo(
    identifier: str = Path(..., description="Código o ObjectId del patólogo"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Obtener un patólogo específico por código o _id."""
    try:
        logger.info(f"Buscando patólogo por identificador: {identifier}")
        return await patologo_service.get_patologo_by_code_or_id(identifier)
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado: {identifier}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado obteniendo patólogo {identifier}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.put("/{patologo_code}", response_model=PatologoResponse)
async def update_patologo(
    patologo_code: str,
    patologo_data: PatologoUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Actualizar un patólogo por código"""
    try:
        logger.info(f"Actualizando patólogo: {patologo_code}")
        return await patologo_service.update_patologo(patologo_code, patologo_data)
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para actualizar: {patologo_code}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        logger.warning(f"Conflicto al actualizar patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Datos inválidos al actualizar patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado actualizando patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.delete("/{patologo_code}", status_code=status.HTTP_200_OK)
async def delete_patologo(
    patologo_code: str,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Eliminar un patólogo por código (soft delete)"""
    try:
        logger.info(f"Eliminando patólogo: {patologo_code}")
        await patologo_service.delete_patologo(patologo_code)
        return {"message": f"Patólogo con código {patologo_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para eliminar: {patologo_code}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al eliminar patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado eliminando patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.put("/{patologo_code}/estado", response_model=PatologoResponse)
async def toggle_estado(
    patologo_code: str,
    estado_data: PatologoEstadoUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Cambiar el estado activo/inactivo de un patólogo por código"""
    try:
        logger.info(f"Cambiando estado de patólogo: {patologo_code} a {estado_data.is_active}")
        return await patologo_service.toggle_estado(patologo_code, estado_data.is_active)
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para cambiar estado: {patologo_code}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al cambiar estado de patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado cambiando estado de patólogo {patologo_code}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get("/{identifier}/firma")
async def get_firma(
    identifier: str,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Obtener solo la firma digital de un patólogo (código o id)."""
    try:
        logger.info(f"Obteniendo firma de patólogo: {identifier}")
        pat = await patologo_service.get_patologo_by_code_or_id(identifier)
        return {
            "patologo_code": pat.patologo_code,
            "firma": pat.firma
        }
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para obtener firma: {identifier}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado obteniendo firma de patólogo {identifier}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.put("/{identifier}/firma", response_model=PatologoResponse)
async def update_firma(
    identifier: str,
    firma_data: PatologoFirmaUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Actualizar la firma digital de un patólogo (código o id)."""
    try:
        logger.info(f"Actualizando firma de patólogo: {identifier}")
        # Resolver a código real
        pat = await patologo_service.get_patologo_by_code_or_id(identifier)
        return await patologo_service.update_firma(pat.patologo_code, firma_data.firma)
    except NotFoundError as e:
        logger.warning(f"Patólogo no encontrado para actualizar firma: {identifier}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        logger.warning(f"Error al actualizar firma de patólogo {identifier}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado actualizando firma de patólogo {identifier}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")