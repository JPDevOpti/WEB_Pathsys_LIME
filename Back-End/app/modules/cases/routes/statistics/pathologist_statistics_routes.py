from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.exceptions import BadRequestError
from app.modules.cases.services.statistics.pathologist_statistics_service import PathologistStatisticsService
from app.modules.cases.repositories.statistics.pathologist_statistics_repository import PathologistStatisticsRepository
from app.config.database import get_database

router = APIRouter(prefix="/pathologists", tags=["Pathologist Statistics"])


async def get_pathologist_statistics_service():
    """Dependency to get pathologist statistics service"""
    database = await get_database()
    repository = PathologistStatisticsRepository(database)
    return PathologistStatisticsService(repository)


@router.get("/monthly-performance")
async def get_monthly_performance(
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., description="Año"),
    thresholdDays: int = Query(7, ge=1, le=60, description="Días de oportunidad"),
    pathologist: str | None = Query(None, description="Nombre del patólogo (opcional)"),
    service: PathologistStatisticsService = Depends(get_pathologist_statistics_service)
):
    """Obtener rendimiento mensual de patólogos"""
    try:
        return await service.get_monthly_performance(month, year, thresholdDays, pathologist)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/entities")
async def get_pathologist_entities(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., description="Año"),
    service: PathologistStatisticsService = Depends(get_pathologist_statistics_service)
):
    """Obtener entidades donde trabaja un patólogo"""
    try:
        return await service.get_pathologist_entities(patologo, month, year)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/tests")
async def get_pathologist_tests(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: int = Query(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(..., description="Año"),
    service: PathologistStatisticsService = Depends(get_pathologist_statistics_service)
):
    """Obtener pruebas realizadas por un patólogo"""
    try:
        return await service.get_pathologist_tests(patologo, month, year)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/opportunity-summary")
async def get_pathologist_opportunity_summary(
    patologo: str = Query(..., description="Nombre del patólogo"),
    thresholdDays: int = Query(7, ge=1, le=60, description="Días de oportunidad"),
    service: PathologistStatisticsService = Depends(get_pathologist_statistics_service)
):
    """Obtener resumen de oportunidad de un patólogo"""
    try:
        return await service.get_pathologist_opportunity_summary(patologo, thresholdDays)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/monthly-trends")
async def get_pathologist_monthly_trends(
    patologo: str = Query(..., description="Nombre del patólogo"),
    year: int = Query(..., description="Año"),
    thresholdDays: int = Query(7, ge=1, le=60, description="Días de oportunidad"),
    service: PathologistStatisticsService = Depends(get_pathologist_statistics_service)
):
    """Obtener tendencias mensuales de un patólogo"""
    try:
        return await service.get_pathologist_monthly_trends(patologo, year, thresholdDays)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

