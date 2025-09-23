from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.dependencies import get_database
from app.modules.casos.repositories.query.urgent_cases_repository import UrgentCasesRepository
from app.modules.casos.services.query.urgent_cases_service import UrgentCasesService
from app.modules.casos.schemas.query.urgent_cases import UrgentCasesRequest, UrgentCasesResponse
from app.modules.casos.services.cache_service import cache_service


router = APIRouter(prefix="/consulta/urgentes", tags=["casos-consulta"])


@router.get("", response_model=UrgentCasesResponse)
async def get_urgent_cases_general(
    limite: int = Query(50, ge=1, le=200, description="Límite de casos a retornar"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Obtiene casos urgentes generales (todos los roles excepto patólogos)"""
    # TODO: Implementar lógica de negocio
    repository = UrgentCasesRepository(db)
    service = UrgentCasesService(repository, cache_service)
    
    request = UrgentCasesRequest(limite=limite)
    return await service.get_urgent_cases(request)


@router.get("/patologo", response_model=UrgentCasesResponse)
async def get_urgent_cases_by_pathologist(
    patologo_code: str = Query(..., description="Código del patólogo"),
    limite: int = Query(50, ge=1, le=200, description="Límite de casos a retornar"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Obtiene casos urgentes por patólogo específico"""
    # TODO: Implementar lógica de negocio
    repository = UrgentCasesRepository(db)
    service = UrgentCasesService(repository, cache_service)
    
    request = UrgentCasesRequest(
        patologo_codigo=patologo_code,
        limite=limite
    )
    return await service.get_urgent_cases(request)


