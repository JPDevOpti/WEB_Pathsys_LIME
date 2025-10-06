"""Rutas API para solicitudes de aprobación."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.approvals.schemas.approval import (
    ApprovalRequestCreate,
    ApprovalRequestUpdate,
    ApprovalRequestResponse,
    ApprovalRequestSearch,
    ApprovalStats,
    ApprovalStateEnum
)
from app.modules.approvals.services.approval_service import ApprovalService
from app.modules.auth.routes.auth_routes import get_current_user_id, get_current_user_id_optional
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["Solicitudes de Aprobación"])




def get_approval_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ApprovalService:
    """Obtener instancia del servicio de aprobaciones."""
    return ApprovalService(db)


@router.post("/", response_model=ApprovalRequestResponse)
async def create_approval_request(
    approval_data: ApprovalRequestCreate,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: Optional[str] = Depends(get_current_user_id_optional)
):
    """
    Crear nueva solicitud de aprobación.
    Usa autenticación opcional para permitir operaciones con tokens expirados.
    """
    try:
        # Log para debugging
        print(f"Creating approval request for case {approval_data.original_case_code}")
        if current_user_id:
            print(f"Requested by user: {current_user_id}")
        else:
            print("User ID not available (token expired or missing)")
        approval = await service.create_approval_request(approval_data)
        return approval
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stats", response_model=ApprovalStats)
async def get_approval_statistics(
    service: ApprovalService = Depends(get_approval_service)
):
    """Obtener estadísticas de solicitudes de aprobación."""
    try:
        stats = await service.get_statistics()
        return stats
    except Exception as e:
        # Log del error para debugging
        print(f"Error en get_statistics: {e}")
        # Si no hay datos, devolver estadísticas vacías
        return ApprovalStats(
            total_requests=0,
            requests_made=0,
            pending_approval=0,
            approved=0,
            rejected=0
        )


@router.get("/{approval_code}", response_model=ApprovalRequestResponse)
async def get_approval_request(
    approval_code: str,
    service: ApprovalService = Depends(get_approval_service)
):
    """Obtener solicitud de aprobación por código."""
    approval = await service.get_approval_by_code(approval_code)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
    return approval


@router.post("/search")
async def search_approval_requests(
    search_params: ApprovalRequestSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: ApprovalService = Depends(get_approval_service)
):
    """Buscar solicitudes de aprobación con filtros."""
    approvals = await service.search_approvals(search_params, skip, limit)
    total = await service.count_approvals(search_params)
    return {
        "data": approvals,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/state/{state}", response_model=List[ApprovalRequestResponse])
async def get_approvals_by_state(
    state: ApprovalStateEnum,
    limit: int = Query(50, ge=1, le=100),
    service: ApprovalService = Depends(get_approval_service)
):
    """Obtener solicitudes por estado."""
    approvals = await service.get_approvals_by_state(state, limit)
    return approvals


@router.patch("/{approval_code}/manage", response_model=ApprovalRequestResponse)
async def manage_approval_request(
    approval_code: str,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Marcar solicitud como en gestión."""
    approval = await service.manage_approval(approval_code)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
    return approval


@router.patch("/{approval_code}/approve")
async def approve_request(
    approval_code: str,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Aprobar solicitud y crear nuevo caso automáticamente."""
    result = await service.approve_request(approval_code)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
    
    return {
        "success": True,
        "message": "Solicitud aprobada y nuevo caso creado exitosamente",
        "data": result
    }


@router.patch("/{approval_code}/reject", response_model=ApprovalRequestResponse)
async def reject_request(
    approval_code: str,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Rechazar solicitud."""
    approval = await service.reject_request(approval_code)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
    return approval


@router.put("/{approval_code}", response_model=ApprovalRequestResponse)
async def update_approval_request(
    approval_code: str,
    update_data: ApprovalRequestUpdate,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Actualizar solicitud de aprobación."""
    try:
        approval = await service.update_approval(approval_code, update_data)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
        return approval
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{approval_code}/tests")
async def update_complementary_tests(
    approval_code: str,
    request_data: dict,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Actualizar pruebas complementarias de una solicitud."""
    try:
        complementary_tests = request_data.get("complementary_tests", [])
        if not complementary_tests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Debe proporcionar al menos una prueba complementaria"
            )
        
        # Validar estructura de las pruebas
        for test in complementary_tests:
            if not all(key in test for key in ["code", "name", "quantity"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Cada prueba debe tener code, name y quantity"
                )
            if not isinstance(test["quantity"], int) or test["quantity"] < 1 or test["quantity"] > 20:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="La cantidad debe ser un número entre 1 y 20"
                )
        
        approval = await service.update_complementary_tests(approval_code, complementary_tests)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
        
        return {
            "success": True,
            "message": "Pruebas complementarias actualizadas exitosamente",
            "data": approval
        }
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{approval_code}")
async def delete_approval_request(
    approval_code: str,
    service: ApprovalService = Depends(get_approval_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Eliminar solicitud de aprobación."""
    success = await service.delete_approval(approval_code)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de aprobación no encontrada")
    
    return {
        "success": True,
        "message": "Solicitud de aprobación eliminada exitosamente"
    }
