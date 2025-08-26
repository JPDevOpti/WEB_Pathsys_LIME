from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.core.exceptions import (
    ConflictError,
    BadRequestError,
    NotFoundError
)
from app.modules.auxiliares.repositories.auxiliar_repository import AuxiliarRepository
from app.modules.auxiliares.services.auxiliar_service import AuxiliarService
from app.modules.auxiliares.schemas.auxiliar import (
    AuxiliarCreate,
    AuxiliarUpdate,
    AuxiliarResponse,
    AuxiliarSearch,
    AuxiliarEstadoUpdate
)
from app.shared.services.user_management import UserManagementService

router = APIRouter(tags=["auxiliares"])

# Dependency para obtener el servicio
def get_auxiliar_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuxiliarService:
    auxiliar_repository = AuxiliarRepository(db)
    user_management_service = UserManagementService(db)
    return AuxiliarService(auxiliar_repository, user_management_service)

@router.post("/", response_model=AuxiliarResponse, status_code=201)
async def create_auxiliar(
    auxiliar_data: AuxiliarCreate,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Crear un nuevo auxiliar"""
    try:
        return await service.create_auxiliar(auxiliar_data)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/", response_model=List[AuxiliarResponse])
async def get_auxiliares(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener lista de auxiliares activos con paginación"""
    try:
        return await service.get_auxiliares(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_auxiliares(
    auxiliarName: str = Query(None, description="Nombre del auxiliar"),
    auxiliarCode: str = Query(None, description="Código del auxiliar"),
    AuxiliarEmail: str = Query(None, description="Email del auxiliar"),
    isActive: bool = Query(None, description="Estado del auxiliar"),
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Buscar auxiliares con filtros avanzados"""
    try:
        search_params = AuxiliarSearch(
            auxiliarName=auxiliarName,
            auxiliarCode=auxiliarCode,
            AuxiliarEmail=AuxiliarEmail,
            isActive=isActive
        )
        
        auxiliares = await service.search_auxiliares(search_params)
        
        return {
            "auxiliares": auxiliares,
            "total": len(auxiliares),
            "filtros_aplicados": {
                "auxiliarName": auxiliarName,
                "auxiliarCode": auxiliarCode,
                "AuxiliarEmail": AuxiliarEmail,
                "isActive": isActive
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/activos", response_model=List[AuxiliarResponse])
async def get_auxiliares_activos(
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener todos los auxiliares activos"""
    try:
        return await service.get_auxiliares_activos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/inactivos", response_model=List[AuxiliarResponse])
async def get_auxiliares_inactivos(
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener todos los auxiliares inactivos"""
    try:
        return await service.get_auxiliares_inactivos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/estadisticas", response_model=Dict[str, Any])
async def get_estadisticas_auxiliares(
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener estadísticas de auxiliares"""
    try:
        return await service.get_estadisticas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{auxiliar_code}", response_model=AuxiliarResponse)
async def get_auxiliar(
    auxiliar_code: str,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Obtener un auxiliar por código"""
    try:
        return await service.get_auxiliar(auxiliar_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{auxiliar_code}", response_model=AuxiliarResponse)
async def update_auxiliar(
    auxiliar_code: str,
    auxiliar_data: AuxiliarUpdate,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Actualizar un auxiliar"""
    try:
        return await service.update_auxiliar(auxiliar_code, auxiliar_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{auxiliar_code}", status_code=200)
async def delete_auxiliar(
    auxiliar_code: str,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Eliminar permanentemente un auxiliar de la base de datos"""
    try:
        success = await service.delete_auxiliar(auxiliar_code)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo eliminar el auxiliar")
        return {"message": f"Auxiliar con código {auxiliar_code} ha sido eliminado correctamente"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{auxiliar_code}/activar", response_model=AuxiliarResponse)
async def activate_auxiliar(
    auxiliar_code: str,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Activar un auxiliar"""
    try:
        return await service.activate_auxiliar(auxiliar_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.patch("/{auxiliar_code}/estado", response_model=AuxiliarResponse)
async def update_auxiliar_estado(
    auxiliar_code: str,
    estado_data: AuxiliarEstadoUpdate,
    service: AuxiliarService = Depends(get_auxiliar_service)
):
    """Actualizar solo el estado de un auxiliar"""
    try:
        auxiliar_update = AuxiliarUpdate(
            auxiliarName=None,
            auxiliarCode=None,
            AuxiliarEmail=None,
            observaciones=None,
            isActive=estado_data.isActive
        )
        return await service.update_auxiliar(auxiliar_code, auxiliar_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")