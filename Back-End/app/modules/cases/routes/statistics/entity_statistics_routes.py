from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.config.database import get_database
from app.modules.cases.repositories.statistics.entity_statistics_repository import EntityStatisticsRepository
from app.modules.cases.services.statistics.entity_statistics_service import EntityStatisticsService
from app.core.exceptions import BadRequestError


router = APIRouter(tags=["statistics-entity"])


def get_entity_statistics_service(db = Depends(get_database)):
    """Servicio de estadísticas de entidades con dependencia de base de datos"""
    repository = EntityStatisticsRepository(db)
    return EntityStatisticsService(repository)


@router.get("/monthly-performance")
async def get_monthly_entity_performance(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    entity: Optional[str] = Query(None, description="Optional entity name filter"),
    service: EntityStatisticsService = Depends(get_entity_statistics_service)
):
    """Get monthly performance statistics for entities"""
    try:
        result = await service.get_monthly_performance(
            month=month,
            year=year,
            entity_name=entity
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/details")
async def get_entity_details(
    entity_name: str = Query(..., alias="entidad", description="Nombre de la entidad"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    service: EntityStatisticsService = Depends(get_entity_statistics_service)
):
    """Obtener estadísticas detalladas para una entidad específica"""
    try:
        result = await service.get_entity_details(
            entity_name=entity_name,
            month=month,
            year=year
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/pathologists")
async def get_entity_pathologists(
    entity_name: str = Query(..., alias="entidad", description="Nombre de la entidad"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    service: EntityStatisticsService = Depends(get_entity_statistics_service)
):
    """Obtener patólogos que trabajan con una entidad específica"""
    try:
        result = await service.get_entity_pathologists(
            entity_name=entity_name,
            month=month,
            year=year
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/debug/unique-entities")
async def debug_unique_entities(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    service: EntityStatisticsService = Depends(get_entity_statistics_service)
):
    """Debug endpoint to see all unique entities in cases"""
    try:
        result = await service.debug_unique_entities(month=month, year=year)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/debug/all-entities-in-cases")
async def debug_all_entities_in_cases(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2030, description="Year"),
    service: EntityStatisticsService = Depends(get_entity_statistics_service)
):
    """Debug endpoint to see ALL entities that have cases (any state)"""
    try:
        result = await service.debug_all_entities_in_cases(month=month, year=year)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")