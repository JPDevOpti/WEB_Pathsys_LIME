from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.modules.cases.services.case_service import CaseService
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.auth.routes.auth_routes import get_current_user_id

# Importar las rutas de resultado y firma
from .result_routes import router as result_router
from .sign_routes import router as sign_router
from .pdf_routes import router as pdf_router
# Importar las rutas de estadísticas
from .statistics.statistics_router import router as statistics_router
from .urgent_routes import router as urgent_router


router = APIRouter(tags=["cases"]) 

# Incluir las rutas de resultado y firma
router.include_router(result_router)
router.include_router(sign_router)
router.include_router(pdf_router)
# Incluir las rutas de estadísticas
router.include_router(statistics_router)
router.include_router(urgent_router)


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


@router.get("/", response_model=List[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0, description="Número de casos a omitir"),
    limit: int = Query(100, ge=1, le=100000, description="Número máximo de casos a retornar"),
    search: Optional[str] = Query(None, description="Búsqueda general por nombre, documento o código de caso"),
    pathologist: Optional[str] = Query(None, description="Filtrar por patólogo asignado"),
    entity: Optional[str] = Query(None, description="Filtrar por entidad"),
    state: Optional[str] = Query(None, description="Filtrar por estado del caso"),
    test: Optional[str] = Query(None, description="Filtrar por prueba específica"),
    date_from: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    service: CaseService = Depends(get_service),
    current_user_id: Optional[str] = Depends(get_current_user_id)
):
    try:
        return await service.list_cases(
            skip=skip,
            limit=limit,
            search=search,
            pathologist=pathologist,
            entity=entity,
            state=state,
            test=test,
            date_from=date_from,
            date_to=date_to,
            current_user_id=current_user_id
        )
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
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


