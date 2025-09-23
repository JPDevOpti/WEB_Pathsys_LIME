"""Rutas de estadísticas para el módulo de casos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any

from app.config.database import get_database
from app.modules.casos.schemas.stats import DashboardMetricsResponse, OpportunityStatsResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(tags=["casos"])  # Se montará bajo el mismo prefijo existente


def get_monthly_stats_service(database: AsyncIOMotorDatabase = Depends(get_database)):
    from app.modules.casos.services.stats.monthly_stats_service import MonthlyStatsService
    return MonthlyStatsService(database)


def get_opportunity_stats_service(database: AsyncIOMotorDatabase = Depends(get_database)):
    from app.modules.casos.services.stats.opportunity_stats_service import OpportunityStatsService
    return OpportunityStatsService(database)


@router.get("/estadisticas/por-mes/{year}", response_model=Dict[str, Any])
async def obtener_casos_por_mes_estadisticas(
    year: int,
    service = Depends(get_monthly_stats_service)
):
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="El año debe estar entre 2020 y 2030")
    return await service.casos_por_mes(year)


@router.get("/estadisticas/por-mes/patologo/{year}", response_model=Dict[str, Any])
async def obtener_casos_por_mes_patologo_estadisticas(
    year: int,
    patologo_codigo: str | None = Query(None, description="Código del patólogo (alias: patologo_code)"),
    patologo_code: str | None = Query(None, description="Código del patólogo (alternativo)"),
    service = Depends(get_monthly_stats_service)
):
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="El año debe estar entre 2020 y 2030")
    code = patologo_codigo or patologo_code
    if not code:
        raise HTTPException(status_code=400, detail="Debe proporcionar patologo_codigo")
    return await service.casos_por_mes_patologo(year, code)


@router.get("/estadisticas/mes-actual", response_model=DashboardMetricsResponse)
async def obtener_mes_actual_estadisticas(
    service = Depends(get_monthly_stats_service)
):
    return await service.mes_actual()


@router.get("/estadisticas/mes-actual/patologo", response_model=DashboardMetricsResponse)
async def obtener_mes_actual_patologo_estadisticas(
    patologo_codigo: str | None = Query(None, description="Código del patólogo (alias: patologo_code)"),
    patologo_code: str | None = Query(None, description="Código del patólogo (alternativo)"),
    service = Depends(get_monthly_stats_service)
):
    code = patologo_codigo or patologo_code
    if not code:
        raise HTTPException(status_code=400, detail="Debe proporcionar patologo_codigo")
    return await service.mes_actual_por_patologo(code)


@router.get("/estadisticas/oportunidad/mes-anterior", response_model=OpportunityStatsResponse)
async def obtener_oportunidad_mes_anterior(
    service = Depends(get_opportunity_stats_service)
):
    return await service.mes_anterior()


@router.get("/estadisticas/oportunidad/mes-anterior/patologo", response_model=OpportunityStatsResponse)
async def obtener_oportunidad_mes_anterior_patologo(
    patologo_codigo: str | None = Query(None, description="Código del patólogo (alias: patologo_code)"),
    patologo_code: str | None = Query(None, description="Código del patólogo (alternativo)"),
    service = Depends(get_opportunity_stats_service)
):
    code = patologo_codigo or patologo_code
    if not code:
        raise HTTPException(status_code=400, detail="Debe proporcionar patologo_codigo")
    return await service.mes_anterior_por_patologo(code)


