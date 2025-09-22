"""Rutas de la API para el módulo de Auxiliaries"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.auxiliaries.services.auxiliar_service import AuxiliarService
from app.modules.auxiliaries.schemas.auxiliar import (
    AuxiliarCreate,
    AuxiliarUpdate,
    AuxiliarResponse,
    AuxiliarSearch
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["auxiliaries"])

# Dependency para obtener el servicio de auxiliaries
async def get_auxiliar_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> AuxiliarService:
    """Obtener instancia del servicio de auxiliaries"""
    return AuxiliarService(database)

@router.post("/", response_model=AuxiliarResponse, status_code=status.HTTP_201_CREATED)
async def create_auxiliar(
    auxiliar: AuxiliarCreate,
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Crear un nuevo auxiliar"""
    try:
        return await auxiliar_service.create_auxiliar(auxiliar)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=List[AuxiliarResponse])
async def list_auxiliaries(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Listar auxiliares activos"""
    try:
        return await auxiliar_service.list_auxiliaries(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/search", response_model=List[AuxiliarResponse])
async def search_auxiliaries(
    q: str = Query(None, description="Término de búsqueda general"),
    auxiliar_name: str = Query(None, description="Filtrar por nombre"),
    auxiliar_code: str = Query(None, description="Filtrar por código"),
    auxiliar_email: str = Query(None, description="Filtrar por email"),
    is_active: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Buscar auxiliares"""
    try:
        search_params = AuxiliarSearch(
            q=q,
            auxiliar_name=auxiliar_name,
            auxiliar_code=auxiliar_code,
            auxiliar_email=auxiliar_email,
            is_active=is_active
        )
        return await auxiliar_service.search_auxiliaries(search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{auxiliar_code}", response_model=AuxiliarResponse)
async def get_auxiliar(
    auxiliar_code: str,
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener auxiliar por código"""
    try:
        return await auxiliar_service.get_auxiliar(auxiliar_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{auxiliar_code}", response_model=AuxiliarResponse)
async def update_auxiliar(
    auxiliar_code: str,
    auxiliar: AuxiliarUpdate,
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Actualizar auxiliar por código"""
    try:
        return await auxiliar_service.update_auxiliar(auxiliar_code, auxiliar)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{auxiliar_code}")
async def delete_auxiliar(
    auxiliar_code: str,
    auxiliar_service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Eliminar auxiliar por código"""
    try:
        result = await auxiliar_service.delete_auxiliar(auxiliar_code)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
