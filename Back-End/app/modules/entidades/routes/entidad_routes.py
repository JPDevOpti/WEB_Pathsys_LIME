from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.entidades.models.entidad import (
    EntidadCreate,
    EntidadUpdate,
    EntidadResponse,
    EntidadSearch
)
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
from app.modules.entidades.services.entidad_service import EntidadService
from app.config.database import get_database

router = APIRouter(tags=["entidades"])


def get_entidad_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> EntidadService:
    """Dependency para obtener el servicio de entidades"""
    repository = EntidadRepository(db)
    return EntidadService(repository)


@router.post("/", response_model=EntidadResponse, status_code=201)
async def create_entidad(
    entidad_data: EntidadCreate,
    service: EntidadService = Depends(get_entidad_service)
):
    """Crear una nueva entidad"""
    return await service.create_entidad(entidad_data)


@router.get("/", response_model=Dict[str, Any])
async def get_entidades(
    query: str = Query(None, description="Término de búsqueda"),
    activo: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    service: EntidadService = Depends(get_entidad_service)
):
    """Obtener lista de entidades con filtros y paginación"""
    search_params = EntidadSearch(
        query=query,
        activo=activo,
        skip=skip,
        limit=limit
    )
    return await service.get_all_entidades(search_params)


@router.get("/code/{code}", response_model=EntidadResponse)
async def get_entidad_by_code(
    code: str,
    service: EntidadService = Depends(get_entidad_service)
):
    """Obtener entidad por código"""
    entidad = await service.get_entidad_by_code(code)
    if not entidad:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    return entidad


@router.put("/code/{code}", response_model=EntidadResponse)
async def update_entidad_by_code(
    code: str,
    entidad_update: EntidadUpdate,
    service: EntidadService = Depends(get_entidad_service)
):
    """Actualizar una entidad por código"""
    return await service.update_entidad_by_code(code, entidad_update)


@router.delete("/code/{code}", status_code=204)
async def delete_entidad_by_code(
    code: str,
    service: EntidadService = Depends(get_entidad_service)
):
    """Eliminar una entidad por código (eliminación permanente)"""
    success = await service.delete_entidad_by_code(code)
    if not success:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")


@router.patch("/code/{code}/toggle-active", status_code=204)
async def toggle_active_entidad_by_code(
    code: str,
    service: EntidadService = Depends(get_entidad_service)
):
    """Cambiar estado activo/inactivo de una entidad por código"""
    success = await service.toggle_active_entidad_by_code(code)
    if not success:
        raise HTTPException(status_code=404, detail="Entidad no encontrada") 