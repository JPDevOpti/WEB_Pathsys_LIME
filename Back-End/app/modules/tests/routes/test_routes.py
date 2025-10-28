from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import TestCreate, TestUpdate, TestResponse, TestSearch
from ..services import get_test_service, TestService
from app.config.database import get_database
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(tags=["tests"])

def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> TestService:
    return get_test_service(database)

@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(test: TestCreate, service: TestService = Depends(get_service)):
    try:
        return await service.create_test(test)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[TestResponse])
async def list_active_tests(
    query: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: TestService = Depends(get_service)
):
    try:
        return await service.list_active(TestSearch(query=query, skip=skip, limit=limit))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/inactive", response_model=List[TestResponse])
async def list_all_tests(
    query: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: TestService = Depends(get_service)
):
    try:
        return await service.list_all(TestSearch(query=query, skip=skip, limit=limit))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{test_code}", response_model=TestResponse)
async def get_test(test_code: str, service: TestService = Depends(get_service)):
    try:
        return await service.get_by_code(test_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{test_code}", response_model=TestResponse)
async def update_test(test_code: str, test_update: TestUpdate, service: TestService = Depends(get_service)):
    try:
        return await service.update_by_code(test_code, test_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{test_code}", response_model=dict)
async def delete_test(test_code: str, service: TestService = Depends(get_service)):
    try:
        success = await service.delete_by_code(test_code)
        if success:
            return {"message": f"Prueba {test_code} eliminada exitosamente"}
        raise HTTPException(status_code=404, detail="Prueba no encontrada")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
