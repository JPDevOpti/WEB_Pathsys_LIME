"""Rutas para el dashboard"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.dependencies import get_current_active_user, require_patologo, get_database
from app.modules.auth.models.auth import AuthUser
from app.modules.dashboard.services.dashboard_service import DashboardService
from app.modules.dashboard.schemas.dashboard import DashboardMetrics
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Dashboard"])

def get_dashboard_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> DashboardService:
    """Dependencia para obtener el servicio del dashboard"""
    return DashboardService(db)

@router.get("/metricas", response_model=DashboardMetrics)
async def get_metricas_dashboard(
    current_user: AuthUser = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Obtener métricas generales del dashboard"""
    try:
        return await dashboard_service.get_metricas_dashboard()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@router.get("/metricas/patologo", response_model=DashboardMetrics)
async def get_metricas_patologo(
    current_user: AuthUser = Depends(require_patologo),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Obtener métricas específicas del patólogo autenticado"""
    try:
        return await dashboard_service.get_metricas_patologo(current_user.email)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo métricas del patólogo: {str(e)}"
        )

@router.get("/casos-por-mes/patologo/{year}")
async def get_casos_por_mes_patologo(
    year: int,
    current_user: AuthUser = Depends(require_patologo),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Obtener casos por mes específicos del patólogo autenticado"""
    try:
        if year < 2020 or year > 2030:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El año debe estar entre 2020 y 2030"
            )
        
        return await dashboard_service.get_casos_por_mes_patologo(current_user.email, year)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo casos por mes del patólogo: {str(e)}"
        )
