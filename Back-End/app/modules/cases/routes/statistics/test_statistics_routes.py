from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.cases.repositories.statistics.test_statistics_repository import TestStatisticsRepository
from app.modules.cases.services.statistics.test_statistics_service import TestStatisticsService
from app.modules.cases.schemas.statistics.test_statistics_schemas import (
    MonthlyTestPerformanceResponse,
    TestDetailsResponse,
    TestPathologistsResponse,
    TestOpportunityResponse,
    TestMonthlyTrendsResponse
)
from app.core.exceptions import BadRequestError

router = APIRouter(tags=["statistics-test"])


def get_test_statistics_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Servicio de estadísticas de pruebas con dependencia de base de datos"""
    repository = TestStatisticsRepository(db)
    return TestStatisticsService(repository)


@router.get("/monthly-performance", response_model=MonthlyTestPerformanceResponse)
async def get_monthly_test_performance(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: TestStatisticsService = Depends(get_test_statistics_service)
):
    """Get monthly performance statistics for all tests"""
    try:
        result = await service.get_monthly_test_performance(month, year, entity)
        return MonthlyTestPerformanceResponse(**result)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/details/{test_code}", response_model=TestDetailsResponse)
async def get_test_details(
    test_code: str,
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: TestStatisticsService = Depends(get_test_statistics_service)
):
    """Get detailed statistics for a specific test"""
    try:
        result = await service.get_test_details(test_code, month, year, entity)
        return TestDetailsResponse(**result)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/pathologists/{test_code}", response_model=TestPathologistsResponse)
async def get_test_pathologists(
    test_code: str,
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: TestStatisticsService = Depends(get_test_statistics_service)
):
    """Get pathologists who worked on a specific test"""
    try:
        result = await service.get_test_pathologists(test_code, month, year, entity)
        return TestPathologistsResponse(pathologists=result)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/opportunity-summary", response_model=TestOpportunityResponse)
async def get_test_opportunity_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    threshold_days: int = Query(7, ge=1, le=60, alias="thresholdDays", description="Opportunity threshold in days"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: TestStatisticsService = Depends(get_test_statistics_service)
):
    """Get opportunity summary for tests"""
    try:
        result = await service.get_test_opportunity_summary(month, year, threshold_days, entity)
        return TestOpportunityResponse(**result)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/monthly-trends", response_model=TestMonthlyTrendsResponse)
async def get_test_monthly_trends(
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: TestStatisticsService = Depends(get_test_statistics_service)
):
    """Get monthly trends for tests"""
    try:
        result = await service.get_test_monthly_trends(year, entity)
        return TestMonthlyTrendsResponse(trends=result)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")