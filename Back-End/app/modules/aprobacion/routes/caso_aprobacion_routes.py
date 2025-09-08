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
    try:
        usuario_id = current_user.id
        caso = await service.create_caso_aprobacion(caso_data, usuario_id)
        return create_response(data=caso, message="Caso de aprobación creado exitosamente")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{caso_id}", response_model=ResponseModel[CasoAprobacionResponse])
async def get_caso_aprobacion(
    caso_id: str,
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    caso = await service.get_caso_by_id(caso_id)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data=caso)


@router.post("/search", response_model=PaginatedResponse[CasoAprobacionResponse])
async def search_casos_aprobacion(
    search_params: CasoAprobacionSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    casos = await service.search_casos(search_params, skip, limit)
    total = await service.count_casos(search_params)
    return create_paginated_response(data=casos, total=total, skip=skip, limit=limit, message="Casos obtenidos")


@router.get("/estado/{estado}", response_model=ResponseModel[List[CasoAprobacionResponse]])
async def get_casos_by_estado(
    estado: EstadoAprobacionEnum,
    limit: int = Query(50, ge=1, le=100),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    casos = await service.get_casos_by_estado(estado, limit)
    return create_response(data=casos, message=f"Casos en estado {estado.value} obtenidos exitosamente")


@router.patch("/{caso_id}/gestionar", response_model=ResponseModel[CasoAprobacionResponse])
async def gestionar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    usuario_id = current_user.id
    caso = await service.gestionar_caso(caso_id, usuario_id, comentarios)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data=caso, message="Caso marcado como en gestión exitosamente")


@router.patch("/{caso_id}/aprobar", response_model=ResponseModel[CasoAprobacionResponse])
async def aprobar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    usuario_id = current_user.id
    caso = await service.aprobar_caso(caso_id, usuario_id, comentarios)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data=caso, message="Caso aprobado exitosamente")


@router.patch("/{caso_id}/rechazar", response_model=ResponseModel[CasoAprobacionResponse])
async def rechazar_caso(
    caso_id: str,
    comentarios: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    usuario_id = current_user.id
    caso = await service.rechazar_caso(caso_id, usuario_id, comentarios)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data=caso, message="Caso rechazado exitosamente")


@router.put("/{caso_id}", response_model=ResponseModel[CasoAprobacionResponse])
async def update_caso_aprobacion(
    caso_id: str,
    caso_data: CasoAprobacionUpdate,
    current_user: AuthUser = Depends(get_current_user),
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    usuario_id = current_user.id
    caso = await service.update_caso(caso_id, caso_data, usuario_id)
    if not caso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data=caso, message="Caso de aprobación actualizado exitosamente")


@router.delete("/{caso_id}", response_model=ResponseModel[dict])
async def delete_caso_aprobacion(
    caso_id: str,
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    success = await service.delete_caso(caso_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso de aprobación no encontrado")
    return create_response(data={"deleted": True}, message="Caso de aprobación eliminado exitosamente")


@router.get("/estadisticas/general", response_model=ResponseModel[CasoAprobacionStats])
async def get_estadisticas_aprobacion(
    service: CasoAprobacionService = Depends(get_caso_aprobacion_service)
):
    stats = await service.get_estadisticas()
    return create_response(data=stats, message="Estadísticas de casos de aprobación obtenidas exitosamente")
