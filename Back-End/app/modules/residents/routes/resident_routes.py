"""Rutas de la API para el módulo de Residents"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.residents.services.resident_service import ResidentService
from app.modules.residents.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    ResidentResponse,
    ResidentSearch
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["residents"])

# Dependency para obtener el servicio de residents
async def get_resident_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> ResidentService:
    """Obtener instancia del servicio de residents"""
    return ResidentService(database)

@router.post("/", response_model=ResidentResponse, status_code=status.HTTP_201_CREATED)
async def create_resident(
    resident: ResidentCreate,
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Crear un nuevo residente"""
    try:
        return await resident_service.create_resident(resident)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=List[ResidentResponse])
async def list_residents(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Listar residentes activos"""
    try:
        return await resident_service.list_residents(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/search", response_model=List[ResidentResponse])
async def search_residents(
    q: str = Query(None, description="Término de búsqueda general"),
    resident_name: str = Query(None, description="Filtrar por nombre"),
    resident_code: str = Query(None, description="Filtrar por código"),
    resident_email: str = Query(None, description="Filtrar por email"),
    medical_license: str = Query(None, description="Filtrar por licencia médica"),
    is_active: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Buscar residentes"""
    try:
        search_params = ResidentSearch(
            q=q,
            resident_name=resident_name,
            resident_code=resident_code,
            resident_email=resident_email,
            medical_license=medical_license,
            is_active=is_active
        )
        return await resident_service.search_residents(search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{resident_code}", response_model=ResidentResponse)
async def get_resident(
    resident_code: str,
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Obtener residente por código"""
    try:
        return await resident_service.get_resident(resident_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{resident_code}", response_model=ResidentResponse)
async def update_resident(
    resident_code: str,
    resident: ResidentUpdate,
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Actualizar residente por código"""
    try:
        return await resident_service.update_resident(resident_code, resident)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{resident_code}")
async def delete_resident(
    resident_code: str,
    resident_service: ResidentService = Depends(get_resident_service)
):
    """Eliminar residente por código"""
    try:
        result = await resident_service.delete_resident(resident_code)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
