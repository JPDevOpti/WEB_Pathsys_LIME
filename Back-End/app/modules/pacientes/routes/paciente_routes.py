import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.pacientes.schemas import PacienteCreate, PacienteUpdate, PacienteResponse, PacienteSearch, Sexo, TipoAtencion
from ..services import get_paciente_service, PacienteService
from app.config.database import get_database
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError

logger = logging.getLogger(__name__)


router = APIRouter(tags=["pacientes"])

def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> PacienteService:
    return get_paciente_service(database)


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def create_paciente(paciente: PacienteCreate, service: PacienteService = Depends(get_service)):
    try:
        return await service.create_paciente(paciente)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/", response_model=List[PacienteResponse])
async def list_pacientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    buscar: Optional[str] = Query(None),
    entidad: Optional[str] = Query(None),
    sexo: Optional[Sexo] = Query(None),
    tipo_atencion: Optional[TipoAtencion] = Query(None),
    service: PacienteService = Depends(get_service)
):
    try:
        return await service.list_pacientes(skip=skip, limit=limit, buscar=buscar, entidad=entidad, sexo=sexo, tipo_atencion=tipo_atencion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/buscar/avanzada", response_model=Dict[str, Any])
async def advanced_search(
    nombre: Optional[str] = Query(None),
    paciente_code: Optional[str] = Query(None),
    edad_min: Optional[int] = Query(None, ge=0, le=150),
    edad_max: Optional[int] = Query(None, ge=0, le=150),
    entidad: Optional[str] = Query(None),
    sexo: Optional[Sexo] = Query(None),
    tipo_atencion: Optional[TipoAtencion] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PacienteService = Depends(get_service)
):
    try:
        search_params = PacienteSearch(
            nombre=nombre, paciente_code=paciente_code, edad_min=edad_min, edad_max=edad_max,
            entidad=entidad, sexo=sexo, tipo_atencion=tipo_atencion,
            fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, skip=skip, limit=limit
        )
        return await service.advanced_search(search_params)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")




@router.get("/entidades/lista", response_model=List[str])
async def get_entidades_list(service: PacienteService = Depends(get_service)):
    try:
        return await service.get_entidades_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/count", response_model=Dict[str, int])
async def get_total_count(service: PacienteService = Depends(get_service)):
    try:
        total = await service.get_total_count()
        return {"total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")




@router.get("/documento/{documento}", response_model=PacienteResponse)
async def get_paciente_by_documento(documento: str, service: PacienteService = Depends(get_service)):
    try:
        return await service.get_paciente_by_id(documento)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{paciente_id}", response_model=PacienteResponse)
async def get_paciente(paciente_id: str, service: PacienteService = Depends(get_service)):
    try:
        return await service.get_paciente_by_id(paciente_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def update_paciente(paciente_id: str, paciente_update: PacienteUpdate, service: PacienteService = Depends(get_service)):
    try:
        return await service.update_paciente(paciente_id, paciente_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{paciente_id}/change-code", response_model=PacienteResponse)
async def change_patient_code(paciente_id: str, new_code: str = Query(...), service: PacienteService = Depends(get_service)):
    try:
        return await service.change_patient_code(paciente_id, new_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{paciente_id}", response_model=Dict[str, str])
async def delete_paciente(paciente_id: str, service: PacienteService = Depends(get_service)):
    try:
        success = await service.delete_paciente(paciente_id)
        if success:
            return {"message": f"Paciente {paciente_id} eliminado exitosamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar el paciente")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

