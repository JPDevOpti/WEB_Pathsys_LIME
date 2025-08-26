from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
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
        return await service.create_residente(residente_data)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/", response_model=List[ResidenteResponse])
async def get_residentes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: ResidenteService = Depends(get_residente_service)
):
    """Obtener lista de residentes activos con paginación"""
    try:
        return await service.get_residentes(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_residentes(
    residenteName: str = Query(None, description="Nombre del residente"),
    InicialesResidente: str = Query(None, description="Iniciales del residente"),
    residenteCode: str = Query(None, description="Código del residente"),
    ResidenteEmail: str = Query(None, description="Email del residente"),
    registro_medico: str = Query(None, description="Registro médico"),
    isActive: bool = Query(None, description="Estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: ResidenteService = Depends(get_residente_service)
):
    """Búsqueda avanzada de residentes"""
    try:
        search_params = ResidenteSearch(
            residenteName=residenteName,
            InicialesResidente=InicialesResidente,
            residenteCode=residenteCode,
            ResidenteEmail=ResidenteEmail,
            registro_medico=registro_medico,
            isActive=isActive
        )
        return await service.search_residentes(search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{residente_code}", response_model=ResidenteResponse)
async def get_residente(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Obtener un residente por código"""
    try:
        return await service.get_residente(residente_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{residente_code}", response_model=ResidenteResponse)
async def update_residente(
    residente_code: str,
    residente_data: ResidenteUpdate,
    service: ResidenteService = Depends(get_residente_service)
):
    """Actualizar un residente por código"""
    try:
        return await service.update_residente(residente_code, residente_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{residente_code}", status_code=200)
async def delete_residente(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Eliminar (soft delete) un residente por código"""
    try:
        await service.delete_residente(residente_code)
        return {"message": f"Residente con código {residente_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{residente_code}/toggle-estado", response_model=ResidenteResponse)
async def toggle_estado(
    residente_code: str,
    service: ResidenteService = Depends(get_residente_service)
):
    """Cambiar el estado activo/inactivo de un residente"""
    try:
        return await service.toggle_estado(residente_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{residente_code}/estado", response_model=ResidenteResponse)
async def cambiar_estado(
    residente_code: str,
    estado_data: ResidenteEstadoUpdate,
    service: ResidenteService = Depends(get_residente_service)
):
    """Cambiar el estado de un residente (PUT endpoint)"""
    try:
        # Obtener el residente actual
        residente_response = await service.get_residente(residente_code)
        
        # Crear ResidenteUpdate con el nuevo estado
        residente_update = ResidenteUpdate(
            residenteName=residente_response.residenteName,
            InicialesResidente=residente_response.InicialesResidente,
            residenteCode=residente_response.residenteCode,
            ResidenteEmail=residente_response.ResidenteEmail,
            registro_medico=residente_response.registro_medico,
            observaciones=residente_response.observaciones,
            isActive=estado_data.isActive
        )
        
        return await service.update_residente(residente_code, residente_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")