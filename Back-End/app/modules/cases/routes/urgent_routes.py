from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.services.urgent_cases_service import UrgentCasesService


router = APIRouter(tags=["urgent"])


def get_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UrgentCasesService:
    return UrgentCasesService(db)


@router.get("/urgent")
async def list_urgent_cases(
    limit: int = Query(50, ge=1, le=1000, description="Máximo de casos a retornar"),
    min_days: int = Query(6, ge=1, le=365, description="Días hábiles mínimos en estado pendiente"),
    service: UrgentCasesService = Depends(get_service)
):
    try:
        cases = await service.list_urgent(limit=limit, min_days=min_days)
        return {"cases": cases, "count": len(cases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando casos urgentes: {str(e)}")


@router.get("/urgent/pathologist")
async def list_urgent_cases_by_pathologist(
    code: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=1000, description="Máximo de casos a retornar"),
    min_days: int = Query(6, ge=1, le=365, description="Días hábiles mínimos en estado pendiente"),
    service: UrgentCasesService = Depends(get_service)
):
    try:
        cases = await service.list_urgent_by_pathologist(code=code, limit=limit, min_days=min_days)
        return {"cases": cases, "count": len(cases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando casos urgentes por patólogo: {str(e)}")


