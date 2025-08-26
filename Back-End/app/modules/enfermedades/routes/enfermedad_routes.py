from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_database
from app.modules.enfermedades.repositories.enfermedad_repository import EnfermedadRepository
from app.modules.enfermedades.services.enfermedad_service import EnfermedadService
from app.modules.enfermedades.models.enfermedad import EnfermedadCreate, EnfermedadUpdate
from app.modules.enfermedades.schemas.enfermedad_schema import (
    EnfermedadCreateSchema,
    EnfermedadUpdateSchema,
    EnfermedadResponseSchema,
    EnfermedadListResponseSchema,
    EnfermedadSearchResponseSchema,
    EnfermedadByTablaResponseSchema
)

router = APIRouter(tags=["Enfermedades"])


def get_enfermedad_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> EnfermedadService:
    """Dependency para obtener el servicio de enfermedades"""
    repository = EnfermedadRepository(db)
    return EnfermedadService(repository)


@router.post("/", response_model=EnfermedadResponseSchema)
async def create_enfermedad(
    enfermedad_data: EnfermedadCreateSchema,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Crear una nueva enfermedad
    
    **Ejemplo de uso:**
    ```json
    {
        "tabla": "CIE10",
        "codigo": "A000",
        "nombre": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        "descripcion": "COLERA",
        "isActive": true
    }
    ```
    """
    enfermedad = EnfermedadCreate(**enfermedad_data.dict())
    return await service.create_enfermedad(enfermedad)


@router.get("/", response_model=EnfermedadListResponseSchema)
async def get_all_enfermedades(
    skip: int = Query(0, ge=0, description="Número de elementos a omitir"),
    limit: int = Query(100, ge=1, le=15000, description="Número máximo de elementos a retornar"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Obtener todas las enfermedades con paginación
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades?skip=0&limit=50&is_active=true
    ```
    """
    result = await service.get_all_enfermedades(skip, limit, is_active)
    return result


@router.get("/search/nombre", response_model=EnfermedadSearchResponseSchema)
async def search_enfermedades_by_name(
    q: str = Query(..., min_length=1, description="Término de búsqueda por nombre"),
    skip: int = Query(0, ge=0, description="Número de elementos a omitir"),
    limit: int = Query(100, ge=1, le=15000, description="Número máximo de elementos a retornar"),
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Buscar enfermedades por nombre
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades/search/nombre?q=COLERA&skip=0&limit=20
    ```
    """
    result = await service.search_enfermedades_by_name(q, skip, limit)
    return result


@router.get("/search/codigo", response_model=EnfermedadSearchResponseSchema)
async def search_enfermedades_by_codigo(
    q: str = Query(..., min_length=1, description="Término de búsqueda por código"),
    skip: int = Query(0, ge=0, description="Número de elementos a omitir"),
    limit: int = Query(100, ge=1, le=15000, description="Número máximo de elementos a retornar"),
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Buscar enfermedades por código
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades/search/codigo?q=A00&skip=0&limit=20
    ```
    """
    result = await service.search_enfermedades_by_codigo(q, skip, limit)
    return result


@router.get("/tabla/{tabla}", response_model=EnfermedadByTablaResponseSchema)
async def get_enfermedades_by_tabla(
    tabla: str,
    skip: int = Query(0, ge=0, description="Número de elementos a omitir"),
    limit: int = Query(100, ge=1, le=15000, description="Número máximo de elementos a retornar"),
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Obtener enfermedades por tabla de referencia
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades/tabla/CIE10?skip=0&limit=50
    ```
    """
    result = await service.get_enfermedades_by_tabla(tabla, skip, limit)
    return result


@router.get("/codigo/{codigo}", response_model=EnfermedadResponseSchema)
async def get_enfermedad_by_codigo(
    codigo: str,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Obtener una enfermedad por su código
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades/codigo/A000
    ```
    """
    enfermedad = await service.get_enfermedad_by_codigo(codigo)
    if not enfermedad:
        raise HTTPException(status_code=404, detail=f"Enfermedad con código {codigo} no encontrada")
    return enfermedad


@router.get("/{enfermedad_id}", response_model=EnfermedadResponseSchema)
async def get_enfermedad_by_id(
    enfermedad_id: str,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Obtener una enfermedad por su ID
    
    **Ejemplo de uso:**
    ```
    GET /enfermedades/507f1f77bcf86cd799439011
    ```
    """
    enfermedad = await service.get_enfermedad_by_id(enfermedad_id)
    if not enfermedad:
        raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
    return enfermedad


@router.put("/{enfermedad_id}", response_model=EnfermedadResponseSchema)
async def update_enfermedad(
    enfermedad_id: str,
    enfermedad_data: EnfermedadUpdateSchema,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Actualizar una enfermedad existente
    
    **Ejemplo de uso:**
    ```json
    {
        "nombre": "Nuevo nombre de la enfermedad",
        "descripcion": "Nueva descripción"
    }
    ```
    """
    enfermedad_update = EnfermedadUpdate(**enfermedad_data.dict(exclude_unset=True))
    return await service.update_enfermedad(enfermedad_id, enfermedad_update)


@router.delete("/{enfermedad_id}")
async def delete_enfermedad(
    enfermedad_id: str,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Eliminar una enfermedad (soft delete)
    
    **Ejemplo de uso:**
    ```
    DELETE /enfermedades/507f1f77bcf86cd799439011
    ```
    """
    await service.delete_enfermedad(enfermedad_id)
    return {"message": "Enfermedad eliminada exitosamente"}


@router.delete("/{enfermedad_id}/permanent")
async def hard_delete_enfermedad(
    enfermedad_id: str,
    service: EnfermedadService = Depends(get_enfermedad_service)
):
    """
    Eliminar una enfermedad permanentemente
    
    **Ejemplo de uso:**
    ```
    DELETE /enfermedades/507f1f77bcf86cd799439011/permanent
    ```
    """
    await service.hard_delete_enfermedad(enfermedad_id)
    return {"message": "Enfermedad eliminada permanentemente"}
