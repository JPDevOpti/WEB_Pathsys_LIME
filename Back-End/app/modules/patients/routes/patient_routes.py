from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.patients.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientSearch, Gender, CareType, IdentificationType
from ..services import get_patient_service, PatientService
from app.config.database import get_database
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["patients"])

def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> PatientService:
    return get_patient_service(database)

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, service: PatientService = Depends(get_service)):
    try:
        result = await service.create_patient(patient)
        return result
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("[patients:create] Error interno al crear paciente")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    gender: Optional[Gender] = Query(None),
    care_type: Optional[CareType] = Query(None),
    service: PatientService = Depends(get_service)
):
    try:
        return await service.list_patients(skip=skip, limit=limit, search=search, entity=entity, gender=gender, care_type=care_type)
    except Exception:
        logger.exception("[patients:list] Error interno al listar pacientes")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/advanced", response_model=Dict[str, Any])
async def advanced_search(
    identification_type: Optional[IdentificationType] = Query(None),
    identification_number: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    first_lastname: Optional[str] = Query(None),
    birth_date_from: Optional[str] = Query(None),
    birth_date_to: Optional[str] = Query(None),
    municipality_code: Optional[str] = Query(None),
    municipality_name: Optional[str] = Query(None),
    subregion: Optional[str] = Query(None),
    age_min: Optional[int] = Query(None, ge=0, le=150),
    age_max: Optional[int] = Query(None, ge=0, le=150),
    entity: Optional[str] = Query(None),
    gender: Optional[Gender] = Query(None),
    care_type: Optional[CareType] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PatientService = Depends(get_service)
):
    try:
        search_params = PatientSearch(
            identification_type=identification_type,
            identification_number=identification_number,
            first_name=first_name,
            first_lastname=first_lastname,
            birth_date_from=birth_date_from,
            birth_date_to=birth_date_to,
            municipality_code=municipality_code,
            municipality_name=municipality_name,
            subregion=subregion,
            age_min=age_min,
            age_max=age_max,
            entity=entity,
            gender=gender,
            care_type=care_type,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit
        )
        return await service.advanced_search(search_params)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("[patients:search] Error interno en búsqueda avanzada")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/count", response_model=Dict[str, int])
async def get_total_count(service: PatientService = Depends(get_service)):
    try:
        total = await service.get_total_count()
        return {"total": total}
    except Exception:
        logger.exception("[patients:count] Error obteniendo total de pacientes")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{patient_code}", response_model=PatientResponse)
async def get_patient(patient_code: str, service: PatientService = Depends(get_service)):
    try:
        return await service.get_patient_by_code(patient_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("[patients:get] Error interno al obtener paciente")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{patient_code}", response_model=PatientResponse)
async def update_patient(patient_code: str, patient_update: PatientUpdate, service: PatientService = Depends(get_service)):
    try:
        return await service.update_patient(patient_code, patient_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("[patients:update] Error interno al actualizar paciente")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{patient_code}/change-identification", response_model=PatientResponse)
async def change_patient_identification(
    patient_code: str, 
    new_identification_type: IdentificationType = Query(...),
    new_identification_number: str = Query(...),
    service: PatientService = Depends(get_service)
):
    try:
        return await service.change_patient_identification(patient_code, new_identification_type, new_identification_number)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("[patients:change-id] Error interno al cambiar identificación")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{patient_code}", response_model=Dict[str, str])
async def delete_patient(patient_code: str, service: PatientService = Depends(get_service)):
    try:
        success = await service.delete_patient(patient_code)
        if success:
            return {"message": f"Patient {patient_code} deleted successfully"}
        raise HTTPException(status_code=500, detail="Error deleting patient")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("[patients:delete] Error interno al eliminar paciente")
        raise HTTPException(status_code=500, detail="Internal server error")
