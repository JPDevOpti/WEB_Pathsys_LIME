import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.pruebas.schemas.prueba import (
    PruebaCreate,
    PruebaUpdate,
    PruebaResponse,
    PruebaSearch,
    PruebasListResponse
)
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository
from app.modules.pruebas.services.prueba_service import PruebaService
from app.config.database import get_database

router = APIRouter(tags=["pruebas"])
logger = logging.getLogger(__name__)


def get_prueba_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> PruebaService:
    """Dependency para obtener el servicio de pruebas"""
    repository = PruebaRepository(db)
    return PruebaService(repository)


@router.post("/", response_model=PruebaResponse, status_code=201)
async def create_prueba(
    prueba_data: PruebaCreate,
    service: PruebaService = Depends(get_prueba_service)
):
    """Crear una nueva prueba"""
    try:
        logger.info(f"Creando nueva prueba: {prueba_data.prueba_code}")
        return await service.create_prueba(prueba_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado creando prueba: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/", response_model=PruebasListResponse)
async def get_pruebas(
    query: str = Query(None, description="Término de búsqueda"),
    activo: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=1000, description="Número máximo de registros"),
    service: PruebaService = Depends(get_prueba_service)
):
    """Obtener lista de pruebas con filtros y paginación"""
    try:
        search_params = PruebaSearch(
            query=query,
            activo=activo,
            skip=skip,
            limit=limit
        )
        logger.info(f"Buscando pruebas - query: {query}, activo: {activo}, skip: {skip}, limit: {limit}")
        return await service.get_all_pruebas(search_params)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado obteniendo pruebas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/code/{code}", response_model=PruebaResponse)
async def get_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Obtener prueba por código"""
    try:
        logger.info(f"Buscando prueba por código: {code}")
        prueba = await service.get_prueba_by_code(code)
        if not prueba:
            raise HTTPException(status_code=404, detail="Prueba no encontrada")
        return prueba
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado obteniendo prueba {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put("/code/{code}", response_model=PruebaResponse)
async def update_prueba_by_code(
    code: str,
    prueba_update: PruebaUpdate,
    service: PruebaService = Depends(get_prueba_service)
):
    """Actualizar una prueba por código"""
    try:
        logger.info(f"Actualizando prueba: {code}")
        return await service.update_prueba_by_code(code, prueba_update)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado actualizando prueba {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/code/{code}", status_code=200)
async def delete_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Eliminar una prueba por código (eliminación permanente)"""
    try:
        logger.info(f"Eliminando prueba: {code}")
        success = await service.delete_prueba_by_code(code)
        if not success:
            raise HTTPException(status_code=404, detail="Prueba no encontrada")
        
        return {"message": "Prueba eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado eliminando prueba {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.patch("/code/{code}/toggle-active", status_code=200)
async def toggle_active_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Cambiar estado activo/inactivo de una prueba por código"""
    try:
        logger.info(f"Cambiando estado de prueba: {code}")
        success = await service.toggle_active_prueba_by_code(code)
        if not success:
            raise HTTPException(status_code=404, detail="Prueba no encontrada")
        
        return {"message": "Estado de la prueba cambiado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado cambiando estado de prueba {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )