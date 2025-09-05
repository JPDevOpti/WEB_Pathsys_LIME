"""Rutas API para casos de aprobación"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.modules.auth.models.auth import AuthUser
from app.modules.aprobacion.schemas.caso_aprobacion import (
    CasoAprobacionCreate,
    CasoAprobacionUpdate,
    CasoAprobacionResponse,
    CasoAprobacionSearch,
    CasoAprobacionStats,
    EstadoAprobacionEnum
)
from app.modules.aprobacion.services.caso_aprobacion_service import CasoAprobacionService
from app.core.dependencies import get_caso_aprobacion_service, get_current_user
from app.shared.schemas.responses import (
    ResponseModel,
    PaginatedResponse,
    create_response,
    create_paginated_response
)

router = APIRouter(tags=["Casos de Aprobación"])


@router.post("/", response_model=ResponseModel[CasoAprobacionResponse])
async def create_caso_aprobacion(
    caso_data: CasoAprobacionCreate,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Crear un nuevo caso de aprobación"""
    try:
        usuario_id = current_user.id
        caso = await service.create_caso_aprobacion(caso_data, usuario_id)
        return create_response(
            data=caso,
            message="Caso de aprobación creado exitosamente"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{caso_id}", response_model=ResponseModel[CasoAprobacionResponse])
async def get_caso_aprobacion(
    caso_id: str,
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Obtener caso de aprobación por ID"""
    caso = await service.get_caso_by_id(caso_id)
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    return create_response(data=caso)


@router.get("/codigo/{caso_aprobacion}", response_model=ResponseModel[CasoAprobacionResponse])
async def get_caso_aprobacion_by_codigo(
    caso_aprobacion: str,
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Obtener caso de aprobación por código de aprobación"""
    caso = await service.get_caso_by_codigo(caso_aprobacion)
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso de aprobación {caso_aprobacion} no encontrado"
        )
    return create_response(data=caso)


@router.post("/search/active", response_model=PaginatedResponse[CasoAprobacionResponse])
async def search_casos_aprobacion_active(
    search_params: CasoAprobacionSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Buscar casos de aprobación activos"""
    casos = await service.search_casos_active_only(search_params, skip, limit)
    total = await service.count_casos_active_only(search_params)
    
    return create_paginated_response(
        data=casos,
        total=total,
        skip=skip,
        limit=limit,
        message="Casos de aprobación activos obtenidos exitosamente"
    )


@router.post("/search/all", response_model=PaginatedResponse[CasoAprobacionResponse])
async def search_casos_aprobacion_all(
    search_params: CasoAprobacionSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Buscar todos los casos de aprobación (incluye inactivos)"""
    casos = await service.search_casos_all(search_params, skip, limit)
    total = await service.count_casos_all(search_params)
    
    return create_paginated_response(
        data=casos,
        total=total,
        skip=skip,
        limit=limit,
        message="Todos los casos de aprobación obtenidos exitosamente"
    )


@router.get("/estado/{estado}", response_model=ResponseModel[List[CasoAprobacionResponse]])
async def get_casos_by_estado(
    estado: EstadoAprobacionEnum,
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Obtener casos por estado de aprobación"""
    casos = await service.get_casos_by_estado(estado, limit)
    return create_response(
        data=casos,
        message=f"Casos en estado {estado.value} obtenidos exitosamente"
    )


@router.get("/usuario/{usuario_id}/pendientes", response_model=ResponseModel[List[CasoAprobacionResponse]])
async def get_casos_pendientes_usuario(
    usuario_id: str,
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Obtener casos pendientes para un usuario específico"""
    casos = await service.get_casos_pendientes_usuario(usuario_id, limit)
    return create_response(
        data=casos,
        message=f"Casos pendientes para el usuario {usuario_id} obtenidos exitosamente"
    )


@router.patch("/{caso_id}/gestionar", response_model=ResponseModel[CasoAprobacionResponse])
async def gestionar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Cambiar estado del caso a 'gestionando'"""
    usuario_id = current_user.id
    caso = await service.gestionar_caso(caso_id, usuario_id, comentarios)
    
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    
    return create_response(
        data=caso,
        message="Caso marcado como en gestión exitosamente"
    )


@router.patch("/{caso_id}/aprobar", response_model=ResponseModel[CasoAprobacionResponse])
async def aprobar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Aprobar un caso"""
    usuario_id = current_user.id
    caso = await service.aprobar_caso(caso_id, usuario_id, comentarios)
    
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    
    return create_response(
        data=caso,
        message="Caso aprobado exitosamente"
    )


@router.patch("/{caso_id}/rechazar", response_model=ResponseModel[CasoAprobacionResponse])
async def rechazar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Rechazar un caso"""
    usuario_id = current_user.id
    caso = await service.rechazar_caso(caso_id, usuario_id, comentarios)
    
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    
    return create_response(
        data=caso,
        message="Caso rechazado exitosamente"
    )


@router.put("/{caso_id}", response_model=ResponseModel[CasoAprobacionResponse])
async def update_caso_aprobacion(
    caso_id: str,
    caso_data: CasoAprobacionUpdate,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Actualizar un caso de aprobación"""
    usuario_id = current_user.id
    caso = await service.update_caso(caso_id, caso_data, usuario_id)
    
    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    
    return create_response(
        data=caso,
        message="Caso de aprobación actualizado exitosamente"
    )


@router.delete("/{caso_id}", response_model=ResponseModel[dict])
async def delete_caso_aprobacion(
    caso_id: str,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Eliminación suave de un caso de aprobación"""
    usuario_id = current_user.id
    success = await service.soft_delete_caso(caso_id, usuario_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caso de aprobación no encontrado"
        )
    
    return create_response(
        data={"deleted": True},
        message="Caso de aprobación eliminado exitosamente"
    )


@router.get("/estadisticas/general", response_model=ResponseModel[CasoAprobacionStats])
async def get_estadisticas_aprobacion(
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    """Obtener estadísticas generales de casos de aprobación"""
    stats = await service.get_estadisticas()
    return create_response(
        data=stats,
        message="Estadísticas de casos de aprobación obtenidas exitosamente"
    )
