"""Rutas de la API para el módulo de Patólogos"""

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
from app.core.dependencies import get_database
from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.shared.services.user_management import UserManagementService

router = APIRouter(tags=["patologos"])

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
        return await patologo_service.create_patologo(patologo)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

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
        return await patologo_service.get_patologos(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")


@router.get("/search", response_model=List[PatologoResponse])
async def search_patologos(
    q: Optional[str] = Query(None, description="Término de búsqueda general (nombre, código, email, registro médico)"),
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
            patologoName=None,
            patologoCode=None,
            PatologoEmail=None,
            registro_medico=None,
            isActive=None,
            observaciones=None
        )
        return await patologo_service.search_patologos(search_params=search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")





@router.get("/{patologo_code}", response_model=PatologoResponse)
async def get_patologo(
    patologo_code: str = Path(..., description="Código del patólogo"),
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """
    Obtener un patólogo específico por código
    """
    try:
        return await patologo_service.get_patologo(patologo_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{patologo_code}", response_model=PatologoResponse)
async def update_patologo(
    patologo_code: str,
    patologo_data: PatologoUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Actualizar un patólogo por código"""
    try:
        return await patologo_service.update_patologo(patologo_code, patologo_data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.delete("/{patologo_code}", status_code=status.HTTP_200_OK)
async def delete_patologo(
    patologo_code: str,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Eliminar un patólogo por código (soft delete)"""
    try:
        await patologo_service.delete_patologo(patologo_code)
        return {"message": f"Patólogo con código {patologo_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.put("/{patologo_code}/estado", response_model=PatologoResponse)
async def toggle_estado(
    patologo_code: str,
    estado_data: PatologoEstadoUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Cambiar el estado activo/inactivo de un patólogo por código"""
    try:
        return await patologo_service.toggle_estado(patologo_code, estado_data.isActive)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{patologo_code}/firma", response_model=PatologoResponse)
async def update_firma(
    patologo_code: str,
    firma_data: PatologoFirmaUpdate,
    patologo_service: PatologoService = Depends(get_patologo_service)
):
    """Actualizar la firma digital de un patólogo"""
    try:
        return await patologo_service.update_firma(patologo_code, firma_data.firma)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")