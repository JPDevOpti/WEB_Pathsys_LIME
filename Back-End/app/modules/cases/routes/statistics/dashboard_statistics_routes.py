# Dashboard Statistics Routes
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.schemas.statistics.dashboard_statistics_schemas import (
    CasesByMonthResponse,
    DashboardOverviewResponse,
    MetricsResponse,
    OpportunityResponse
)
from app.modules.cases.services.statistics.dashboard_statistics_service import DashboardStatisticsService
from app.core.exceptions import BadRequestError

router = APIRouter(tags=["statistics-dashboard"])


def get_dashboard_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> DashboardStatisticsService:
    return DashboardStatisticsService(db)


@router.get("/dashboard/cases-by-month/{year}", response_model=CasesByMonthResponse)
async def get_cases_by_month(
    year: int,
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Obtener estadísticas de casos por mes para un año específico
    
    - **year**: Año a consultar (ej: 2025)
    
    Retorna un array de 12 números representando los casos por mes
    """
    try:
        return await service.get_cases_by_month(year)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/dashboard/cases-by-month/pathologist/{year}", response_model=CasesByMonthResponse)
async def get_cases_by_month_pathologist(
    year: int,
    pathologist_code: str = Query(..., description="Código del patólogo"),
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Obtener estadísticas de casos por mes para un patólogo específico
    
    - **year**: Año a consultar (ej: 2025)
    - **pathologist_code**: Código del patólogo (query parameter)
    
    Retorna un array de 12 números representando los casos asignados al patólogo por mes
    """
    try:
        return await service.get_cases_by_month_pathologist(year, pathologist_code)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Obtener resumen general del dashboard
    
    Retorna métricas generales como total de casos, casos del mes actual vs anterior,
    cambio porcentual y distribución por estado
    """
    try:
        return await service.get_dashboard_overview()
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/metrics/general", response_model=MetricsResponse)
async def get_metrics_general(
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Obtener métricas generales del laboratorio
    
    Retorna métricas de pacientes y casos del mes actual vs anterior
    """
    try:
        return await service.get_metrics_general()
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/metrics/pathologist/{pathologist_code}", response_model=MetricsResponse)
async def get_metrics_pathologist(
    pathologist_code: str,
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Obtener métricas específicas de un patólogo
    
    - **pathologist_code**: Código del patólogo
    
    Retorna métricas de pacientes y casos asignados al patólogo del mes actual vs anterior
    """
    try:
        return await service.get_metrics_pathologist(pathologist_code)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/dashboard/validate-pathologist/{pathologist_code}")
async def validate_pathologist(
    pathologist_code: str,
    service: DashboardStatisticsService = Depends(get_dashboard_service)
):
    """
    Validar que un patólogo existe en el sistema
    
    - **pathologist_code**: Código del patólogo a validar
    
    Retorna si el patólogo tiene casos asignados en el sistema
    """
    try:
        exists = await service.validate_pathologist_exists(pathologist_code)
        return {
            "pathologist_code": pathologist_code,
            "exists": exists,
            "message": "Patólogo encontrado" if exists else "Patólogo no encontrado"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


## Eliminado endpoints de oportunidad para rehacerlos
