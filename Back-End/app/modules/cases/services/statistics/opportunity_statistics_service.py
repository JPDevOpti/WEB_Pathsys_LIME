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

    # ---------------------------
    # English responses for v2
    # ---------------------------
    async def get_monthly(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        entity: str = None,
        pathologist: str = None,
    ) -> Dict[str, Any]:
        if month < 1 or month > 12:
            raise BadRequestError("month must be between 1 and 12")
        from datetime import datetime
        current_year = datetime.utcnow().year
        if year < 2020 or year > current_year + 1:
            raise BadRequestError(f"year must be between 2020 and {current_year + 1}")
        if threshold_days < 1 or threshold_days > 60:
            raise BadRequestError("thresholdDays must be between 1 and 60")
        try:
            return await self.repo.get_monthly_opportunity(month, year, threshold_days, entity, pathologist)
        except Exception as e:
            raise BadRequestError(f"Error computing monthly opportunity: {str(e)}")

    async def get_yearly(self, year: int, threshold_days: int = 7) -> Dict[str, Any]:
        from datetime import datetime
        current_year = datetime.utcnow().year
        if year < 2020 or year > current_year + 1:
            raise BadRequestError(f"year must be between 2020 and {current_year + 1}")
        if threshold_days < 1 or threshold_days > 60:
            raise BadRequestError("thresholdDays must be between 1 and 60")
        try:
            arr = await self.repo.get_yearly_opportunity(year, threshold_days)
            return {"percentageByMonth": arr}
        except Exception as e:
            raise BadRequestError(f"Error computing yearly opportunity: {str(e)}")

    async def get_pathologists(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        entity: str = None,
    ) -> Dict[str, Any]:
        data = await self.get_monthly(month, year, threshold_days, entity, None)
        return {"pathologists": data.get("pathologists", [])}

    async def get_tests(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        entity: str = None,
    ) -> Dict[str, Any]:
        data = await self.get_monthly(month, year, threshold_days, entity, None)
        return {"tests": data.get("tests", [])}

