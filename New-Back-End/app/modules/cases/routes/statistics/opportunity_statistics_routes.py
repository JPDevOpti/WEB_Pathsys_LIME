from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.core.exceptions import BadRequestError
from app.modules.cases.schemas.statistics.dashboard_statistics_schemas import OpportunityResponse
from app.modules.cases.services.statistics.opportunity_statistics_service import OpportunityStatisticsService


router = APIRouter(prefix="/opportunity", tags=["opportunity"])


def get_opportunity_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> OpportunityStatisticsService:
    return OpportunityStatisticsService(db)


@router.get("/general", response_model=OpportunityResponse)
async def opportunity_general(
    threshold_days: int = Query(7, ge=1, le=60, description="Días de oportunidad"),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_general(opportunity_days_threshold=threshold_days)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/pathologist/{pathologist_code}", response_model=OpportunityResponse)
async def opportunity_by_pathologist(
    pathologist_code: str,
    threshold_days: int = Query(7, ge=1, le=60, description="Días de oportunidad"),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_by_pathologist(pathologist_code, opportunity_days_threshold=threshold_days)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
