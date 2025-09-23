"""Esquemas Pydantic para el módulo de aprobaciones"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.approvals.models.approval_request import (
    ApprovalStateEnum,
    ComplementaryTestInfo,
    ApprovalInfo
)


class ApprovalRequestCreate(BaseModel):
    """Schema para crear una solicitud de aprobación."""
    original_case_code: str = Field(..., description="Código del caso original")
    complementary_tests: List[ComplementaryTestInfo] = Field(..., description="Pruebas complementarias solicitadas")
    reason: str = Field(..., max_length=1000, description="Motivo de la solicitud")


class ApprovalRequestUpdate(BaseModel):
    """Schema para actualizar una solicitud de aprobación."""
    approval_state: Optional[ApprovalStateEnum] = None
    complementary_tests: Optional[List[ComplementaryTestInfo]] = None


class ApprovalRequestResponse(BaseModel):
    """Schema de respuesta para solicitudes de aprobación."""
    id: str = Field(..., description="ID único de la solicitud")
    approval_code: str = Field(..., description="Código único de la solicitud")
    original_case_code: str = Field(..., description="Código del caso original")
    approval_state: ApprovalStateEnum = Field(..., description="Estado de la aprobación")
    complementary_tests: List[ComplementaryTestInfo] = Field(..., description="Pruebas complementarias")
    approval_info: ApprovalInfo = Field(..., description="Información del proceso")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


class ApprovalRequestSearch(BaseModel):
    """Schema para búsquedas de solicitudes de aprobación."""
    original_case_code: Optional[str] = Field(None, description="Código del caso original")
    approval_state: Optional[ApprovalStateEnum] = None
    request_date_from: Optional[datetime] = None
    request_date_to: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApprovalStats(BaseModel):
    """Schema para estadísticas de solicitudes de aprobación."""
    total_requests: int = 0
    requests_made: int = 0
    pending_approval: int = 0
    approved: int = 0
    rejected: int = 0

    class Config:
        from_attributes = True
