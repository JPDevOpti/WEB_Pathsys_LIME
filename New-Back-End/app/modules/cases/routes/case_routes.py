from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.modules.cases.services.case_service import CaseService
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


router = APIRouter()


def get_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> CaseService:
    return CaseService(db)


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(payload: CaseCreate, service: CaseService = Depends(get_service)):
    try:
        return await service.create_case(payload)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{case_code}", response_model=CaseResponse)
async def update_case(case_code: str, payload: CaseUpdate, service: CaseService = Depends(get_service)):
    try:
        return await service.update_case(case_code, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{case_code}")
async def delete_case(case_code: str, service: CaseService = Depends(get_service)):
    try:
        return await service.delete_case(case_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{case_code}", response_model=CaseResponse)
async def get_case(case_code: str, service: CaseService = Depends(get_service)):
    try:
        return await service.get_case(case_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


