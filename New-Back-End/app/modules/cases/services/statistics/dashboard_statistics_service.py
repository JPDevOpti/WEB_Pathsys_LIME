# Dashboard Statistics Service
from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import BadRequestError
from app.modules.cases.schemas.statistics.dashboard_statistics_schemas import (
    CasesByMonthResponse,
    DashboardOverviewResponse,
    MetricsResponse,
    OpportunityResponse
)
from app.modules.cases.repositories.statistics.dashboard_statistics_repository import DashboardStatisticsRepository


class DashboardStatisticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = DashboardStatisticsRepository(db)

    async def get_cases_by_month(self, year: int) -> CasesByMonthResponse:
        """Obtener estadísticas de casos por mes para un año específico"""
        # Validar año
        current_year = datetime.now().year
        if year < 2020 or year > current_year + 1:
            raise BadRequestError(f"Año debe estar entre 2020 y {current_year + 1}")
        
        try:
            result = await self.repo.get_cases_by_month(year)
            return CasesByMonthResponse(**result)
        except Exception as e:
            raise BadRequestError(f"Error al obtener estadísticas por mes: {str(e)}")

    async def get_cases_by_month_pathologist(self, year: int, pathologist_code: str) -> CasesByMonthResponse:
        """Obtener estadísticas de casos por mes para un patólogo específico"""
        # Validar año
        current_year = datetime.now().year
        if year < 2020 or year > current_year + 1:
            raise BadRequestError(f"Año debe estar entre 2020 y {current_year + 1}")
        
        # Validar código de patólogo
        if not pathologist_code or len(pathologist_code.strip()) == 0:
            raise BadRequestError("Código de patólogo es requerido")
        
        try:
            result = await self.repo.get_cases_by_month_pathologist(year, pathologist_code.strip())
            return CasesByMonthResponse(**result)
        except Exception as e:
            raise BadRequestError(f"Error al obtener estadísticas por mes del patólogo: {str(e)}")

    async def get_dashboard_overview(self) -> DashboardOverviewResponse:
        """Obtener resumen general del dashboard"""
        try:
            result = await self.repo.get_dashboard_overview()
            return DashboardOverviewResponse(**result)
        except Exception as e:
            raise BadRequestError(f"Error al obtener resumen del dashboard: {str(e)}")

    async def get_metrics_general(self) -> MetricsResponse:
        """Obtener métricas generales del laboratorio"""
        try:
            result = await self.repo.get_metrics_general()
            return MetricsResponse(**result)
        except Exception as e:
            raise BadRequestError(f"Error al obtener métricas generales: {str(e)}")

    async def get_metrics_pathologist(self, pathologist_code: str) -> MetricsResponse:
        """Obtener métricas específicas de un patólogo"""
        # Validar código de patólogo
        if not pathologist_code or len(pathologist_code.strip()) == 0:
            raise BadRequestError("Código de patólogo es requerido")
        
        try:
            result = await self.repo.get_metrics_pathologist(pathologist_code.strip())
            return MetricsResponse(**result)
        except Exception as e:
            raise BadRequestError(f"Error al obtener métricas del patólogo: {str(e)}")

    # Eliminadas funciones de oportunidad (se van a rehacer)

    async def validate_pathologist_exists(self, pathologist_code: str) -> bool:
        """Validar que el patólogo existe en el sistema"""
        try:
            # Buscar al menos un caso asignado a este patólogo
            pipeline = [
                {
                    "$match": {
                        "assigned_pathologist.id": pathologist_code
                    }
                },
                {
                    "$limit": 1
                }
            ]
            
            result = await self.repo.collection.aggregate(pipeline).to_list(1)
            return len(result) > 0
        except Exception:
            return False
