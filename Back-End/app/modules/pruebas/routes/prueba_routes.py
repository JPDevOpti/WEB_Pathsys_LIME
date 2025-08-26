from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.pruebas.models.prueba import (
    PruebaCreate,
    PruebaUpdate,
    PruebaResponse,
    PruebaSearch
)
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository
from app.modules.pruebas.services.prueba_service import PruebaService
from app.config.database import get_database

router = APIRouter(tags=["pruebas"])


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
    return await service.create_prueba(prueba_data)


@router.get("/", response_model=Dict[str, Any])
async def get_pruebas(
    query: str = Query(None, description="Término de búsqueda"),
    activo: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=1000, description="Número máximo de registros"),
    service: PruebaService = Depends(get_prueba_service)
):
    """Obtener lista de pruebas con filtros y paginación"""
    search_params = PruebaSearch(
        query=query,
        activo=activo,
        skip=skip,
        limit=limit
    )
    return await service.get_all_pruebas(search_params)


@router.get("/code/{code}", response_model=PruebaResponse)
async def get_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Obtener prueba por código"""
    prueba = await service.get_prueba_by_code(code)
    if not prueba:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")
    return prueba


@router.put("/code/{code}", response_model=PruebaResponse)
async def update_prueba_by_code(
    code: str,
    prueba_update: PruebaUpdate,
    service: PruebaService = Depends(get_prueba_service)
):
    """Actualizar una prueba por código"""
    return await service.update_prueba_by_code(code, prueba_update)


@router.delete("/code/{code}", status_code=204)
async def delete_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Eliminar una prueba por código (eliminación permanente)"""
    success = await service.delete_prueba_by_code(code)
    if not success:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")


@router.patch("/code/{code}/toggle-active", status_code=204)
async def toggle_active_prueba_by_code(
    code: str,
    service: PruebaService = Depends(get_prueba_service)
):
    """Cambiar estado activo/inactivo de una prueba por código"""
    success = await service.toggle_active_prueba_by_code(code)
    if not success:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")