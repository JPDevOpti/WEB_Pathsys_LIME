from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import BadRequestError
from app.modules.cases.repositories.statistics.opportunity_statistics_repository import OpportunityStatisticsRepository
from app.modules.cases.schemas.statistics.dashboard_statistics_schemas import OpportunityResponse, OpportunityMetrics


class OpportunityStatisticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = OpportunityStatisticsRepository(db)

    async def get_general(self, opportunity_days_threshold: int = 7) -> OpportunityResponse:
        try:
            data: Dict[str, Any] = await self.repo.get_opportunity_general(opportunity_days_threshold)
            return OpportunityResponse(oportunity=OpportunityMetrics(**data))
        except Exception as e:
            raise BadRequestError(f"Error obteniendo oportunidad general: {str(e)}")

    async def get_by_pathologist(self, pathologist_code: str, opportunity_days_threshold: int = 7) -> OpportunityResponse:
        if not pathologist_code or len(pathologist_code.strip()) == 0:
            raise BadRequestError("Código de patólogo es requerido")
        try:
            data: Dict[str, Any] = await self.repo.get_opportunity_pathologist(pathologist_code.strip(), opportunity_days_threshold)
            return OpportunityResponse(oportunity=OpportunityMetrics(**data))
        except Exception as e:
            raise BadRequestError(f"Error obteniendo oportunidad por patólogo: {str(e)}")
