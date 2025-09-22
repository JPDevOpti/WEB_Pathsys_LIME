from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.diseases.repositories.disease_repository import DiseaseRepository
from app.modules.diseases.services.disease_service import DiseaseService
from app.modules.diseases.models.disease import DiseaseCreate
from app.modules.diseases.schemas.disease import (
    DiseaseCreateSchema,
    DiseaseResponseSchema,
    DiseaseListResponseSchema,
    DiseaseSearchResponseSchema,
    DiseaseByTableResponseSchema
)

router = APIRouter(tags=["Diseases"])


def get_disease_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> DiseaseService:
    """Dependency to get disease service"""
    repository = DiseaseRepository(db)
    return DiseaseService(repository)


@router.post("/", response_model=DiseaseResponseSchema)
async def create_disease(
    disease_data: DiseaseCreateSchema,
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Create a new disease
    
    **Example usage:**
    ```json
    {
        "table": "CIE10",
        "code": "A000",
        "name": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        "description": "COLERA",
        "is_active": true
    }
    ```
    """
    disease = DiseaseCreate(**disease_data.dict())
    return await service.create_disease(disease)


@router.get("/", response_model=DiseaseListResponseSchema)
async def get_all_diseases(
    skip: int = Query(0, ge=0, description="Number of elements to skip"),
    limit: int = Query(100, ge=1, le=15000, description="Maximum number of elements to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active state"),
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Get all diseases with pagination
    
    **Example usage:**
    ```
    GET /diseases?skip=0&limit=50&is_active=true
    ```
    """
    result = await service.get_all_diseases(skip, limit, is_active)
    return result


@router.get("/search/name", response_model=DiseaseSearchResponseSchema)
async def search_diseases_by_name(
    q: str = Query(..., min_length=1, description="Search term by name"),
    skip: int = Query(0, ge=0, description="Number of elements to skip"),
    limit: int = Query(100, ge=1, le=15000, description="Maximum number of elements to return"),
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Search diseases by name
    
    **Example usage:**
    ```
    GET /diseases/search/name?q=COLERA&skip=0&limit=20
    ```
    """
    result = await service.search_diseases_by_name(q, skip, limit)
    return result


@router.get("/search/code", response_model=DiseaseSearchResponseSchema)
async def search_diseases_by_code(
    q: str = Query(..., min_length=1, description="Search term by code"),
    skip: int = Query(0, ge=0, description="Number of elements to skip"),
    limit: int = Query(100, ge=1, le=15000, description="Maximum number of elements to return"),
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Search diseases by code
    
    **Example usage:**
    ```
    GET /diseases/search/code?q=A00&skip=0&limit=20
    ```
    """
    result = await service.search_diseases_by_code(q, skip, limit)
    return result


@router.get("/table/{table}", response_model=DiseaseByTableResponseSchema)
async def get_diseases_by_table(
    table: str,
    skip: int = Query(0, ge=0, description="Number of elements to skip"),
    limit: int = Query(100, ge=1, le=15000, description="Maximum number of elements to return"),
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Get diseases by reference table
    
    **Example usage:**
    ```
    GET /diseases/table/CIE10?skip=0&limit=50
    ```
    """
    result = await service.get_diseases_by_table(table, skip, limit)
    return result


@router.get("/code/{code}", response_model=DiseaseResponseSchema)
async def get_disease_by_code(
    code: str,
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Get a disease by its code
    
    **Example usage:**
    ```
    GET /diseases/code/A000
    ```
    """
    disease = await service.get_disease_by_code(code)
    if not disease:
        raise HTTPException(status_code=404, detail=f"Disease with code {code} not found")
    return disease


@router.delete("/{disease_id}")
async def delete_disease(
    disease_id: str,
    service: DiseaseService = Depends(get_disease_service)
):
    """
    Delete a disease
    
    **Example usage:**
    ```
    DELETE /diseases/507f1f77bcf86cd799439011
    ```
    """
    await service.delete_disease(disease_id)
    return {"message": "Disease deleted successfully"}
