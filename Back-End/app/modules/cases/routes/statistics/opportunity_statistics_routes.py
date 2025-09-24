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

# ---------------------------
# New English endpoints (v2)
# ---------------------------

@router.get("/monthly")
async def opportunity_monthly(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    thresholdDays: int = Query(7, ge=1, le=60),
    entity: str | None = Query(None),
    pathologist: str | None = Query(None),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_monthly(month, year, thresholdDays, entity, pathologist)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/yearly/{year}")
async def opportunity_yearly(
    year: int,
    thresholdDays: int = Query(7, ge=1, le=60),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_yearly(year, thresholdDays)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/pathologists")
async def opportunity_pathologists(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    thresholdDays: int = Query(7, ge=1, le=60),
    entity: str | None = Query(None),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_pathologists(month, year, thresholdDays, entity)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/tests")
async def opportunity_tests(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    thresholdDays: int = Query(7, ge=1, le=60),
    entity: str | None = Query(None),
    service: OpportunityStatisticsService = Depends(get_opportunity_service)
):
    try:
        return await service.get_tests(month, year, thresholdDays, entity)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
