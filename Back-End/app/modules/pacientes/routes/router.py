"""Router para el módulo de pacientes"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.pacientes.models import (
    PacienteCreate, 
    PacienteUpdate, 
    PacienteResponse, 
    PacienteSearch,
    Sexo,
    TipoAtencion
)
from app.modules.pacientes.schemas import PacienteStats
from ..services import get_paciente_service, PacienteService
from app.config.database import get_database
from app.core.exceptions import NotFoundError, BadRequestError


# Crear el router
router = APIRouter(
    tags=["pacientes"]
)


# Dependency para obtener el servicio
def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> PacienteService:
    return get_paciente_service(database)


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def create_paciente(
    paciente: PacienteCreate,
    service: PacienteService = Depends(get_service)
) -> PacienteResponse:
    """Crear un nuevo paciente"""
    try:
        return await service.create_paciente(paciente)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/", response_model=List[PacienteResponse])
async def list_pacientes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    buscar: Optional[str] = Query(None, description="Buscar por nombre o cédula"),
    entidad: Optional[str] = Query(None, description="Filtrar por entidad"),
    sexo: Optional[Sexo] = Query(None, description="Filtrar por sexo"),
    tipo_atencion: Optional[TipoAtencion] = Query(None, description="Filtrar por tipo de atención"),
    service: PacienteService = Depends(get_service)
) -> List[PacienteResponse]:
    """Listar pacientes con filtros opcionales"""
    try:
        return await service.list_pacientes(
            skip=skip,
            limit=limit,
            buscar=buscar,
            entidad=entidad,
            sexo=sexo,
            tipo_atencion=tipo_atencion
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/buscar/avanzada", response_model=Dict[str, Any])
async def advanced_search(
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    cedula: Optional[str] = Query(None, description="Buscar por cédula"),
    edad_min: Optional[int] = Query(None, ge=0, le=150, description="Edad mínima"),
    edad_max: Optional[int] = Query(None, ge=0, le=150, description="Edad máxima"),
    entidad: Optional[str] = Query(None, description="Filtrar por entidad"),
    sexo: Optional[Sexo] = Query(None, description="Filtrar por sexo"),
    tipo_atencion: Optional[TipoAtencion] = Query(None, description="Filtrar por tipo de atención"),
    tiene_casos: Optional[bool] = Query(None, description="Filtrar por pacientes con/sin casos"),
    fecha_desde: Optional[str] = Query(None, description="Fecha de creación desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha de creación hasta (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: PacienteService = Depends(get_service)
) -> Dict[str, Any]:
    """Búsqueda avanzada de pacientes con múltiples filtros"""
    try:
        search_params = PacienteSearch(
            nombre=nombre,
            cedula=cedula,
            edad_min=edad_min,
            edad_max=edad_max,
            entidad=entidad,
            sexo=sexo,
            tipo_atencion=tipo_atencion,
            tiene_casos=tiene_casos,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            skip=skip,
            limit=limit
        )
        return await service.advanced_search(search_params)
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")





@router.get("/entidades/lista", response_model=List[str])
async def get_entidades_list(
    service: PacienteService = Depends(get_service)
) -> List[str]:
    """Obtener lista de entidades únicas"""
    try:
        return await service.get_entidades_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/count", response_model=Dict[str, int])
async def get_total_count(
    service: PacienteService = Depends(get_service)
) -> Dict[str, int]:
    """Obtener el total de pacientes registrados"""
    try:
        total = await service.get_total_count()
        return {"total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/estadisticas", response_model=PacienteStats)
async def get_statistics(
    service: PacienteService = Depends(get_service)
) -> PacienteStats:
    """Obtener estadísticas generales de pacientes"""
    try:
        return await service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/cedula/{cedula}", response_model=PacienteResponse)
async def get_paciente_by_cedula(
    cedula: str,
    service: PacienteService = Depends(get_service)
) -> PacienteResponse:
    """Buscar un paciente por su número de cédula"""
    try:
        return await service.get_paciente_by_cedula(cedula)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def get_paciente(
    paciente_id: str,
    service: PacienteService = Depends(get_service)
) -> PacienteResponse:
    """Obtener un paciente por su ID"""
    try:
        return await service.get_paciente_by_id(paciente_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def update_paciente(
    paciente_id: str,
    paciente_update: PacienteUpdate,
    service: PacienteService = Depends(get_service)
) -> PacienteResponse:
    """Actualizar un paciente existente"""
    try:
        return await service.update_paciente(paciente_id, paciente_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.delete("/{paciente_id}", response_model=Dict[str, str])
async def delete_paciente(
    paciente_id: str,
    service: PacienteService = Depends(get_service)
) -> Dict[str, str]:
    """Eliminar un paciente"""
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
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.post("/{paciente_id}/casos/{id_caso}", response_model=Dict[str, str])
async def add_caso_to_paciente(
    paciente_id: str,
    id_caso: str,
    service: PacienteService = Depends(get_service)
) -> Dict[str, str]:
    """Agregar un caso a un paciente"""
    try:
        success = await service.add_caso_to_paciente(paciente_id, id_caso)
        if success:
            return {"message": f"Caso {id_caso} agregado al paciente {paciente_id}"}
        else:
            raise HTTPException(status_code=500, detail="Error al agregar el caso")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.delete("/{paciente_id}/casos/{id_caso}", response_model=Dict[str, str])
async def remove_caso_from_paciente(
    paciente_id: str,
    id_caso: str,
    service: PacienteService = Depends(get_service)
) -> Dict[str, str]:
    """Remover un caso de un paciente"""
    try:
        success = await service.remove_caso_from_paciente(paciente_id, id_caso)
        if success:
            return {"message": f"Caso {id_caso} removido del paciente {paciente_id}"}
        else:
            raise HTTPException(status_code=500, detail="Error al remover el caso")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")