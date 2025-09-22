"""Rutas de la API para el módulo de Billing"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.billing.services.billing_service import BillingService
from app.modules.billing.schemas.billing import (
    BillingCreate,
    BillingUpdate,
    BillingResponse,
    BillingSearch
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["billing"])

# Dependency para obtener el servicio de billing
async def get_billing_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> BillingService:
    """Obtener instancia del servicio de billing"""
    return BillingService(database)

@router.post("/", response_model=BillingResponse, status_code=status.HTTP_201_CREATED)
async def create_billing(
    billing: BillingCreate,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Crear un nuevo usuario de facturación"""
    try:
        return await billing_service.create_billing(billing)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=List[BillingResponse])
async def list_billing(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    billing_service: BillingService = Depends(get_billing_service)
):
    """Listar usuarios de facturación activos"""
    try:
        return await billing_service.list_billing(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/search", response_model=List[BillingResponse])
async def search_billing(
    q: str = Query(None, description="Término de búsqueda general"),
    billing_name: str = Query(None, description="Filtrar por nombre"),
    billing_code: str = Query(None, description="Filtrar por código"),
    billing_email: str = Query(None, description="Filtrar por email"),
    is_active: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    billing_service: BillingService = Depends(get_billing_service)
):
    """Buscar usuarios de facturación"""
    try:
        search_params = BillingSearch(
            q=q,
            billing_name=billing_name,
            billing_code=billing_code,
            billing_email=billing_email,
            is_active=is_active
        )
        return await billing_service.search_billing(search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{billing_code}", response_model=BillingResponse)
async def get_billing(
    billing_code: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Obtener usuario de facturación por código"""
    try:
        return await billing_service.get_billing(billing_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{billing_code}", response_model=BillingResponse)
async def update_billing(
    billing_code: str,
    billing: BillingUpdate,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Actualizar usuario de facturación por código"""
    try:
        return await billing_service.update_billing(billing_code, billing)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{billing_code}")
async def delete_billing(
    billing_code: str,
    billing_service: BillingService = Depends(get_billing_service)
):
    """Eliminar usuario de facturación por código"""
    try:
        result = await billing_service.delete_billing(billing_code)
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
