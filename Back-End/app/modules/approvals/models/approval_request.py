"""Modelo para solicitudes de aprobación con pruebas complementarias."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from app.shared.models.base import PyObjectId


class ApprovalStateEnum(str, Enum):
    """Estados del flujo de aprobación."""
    REQUEST_MADE = "request_made"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ComplementaryTestInfo(BaseModel):
    """Información de una prueba complementaria."""
    code: str = Field(..., description="Código de la prueba")
    name: str = Field(..., description="Nombre de la prueba")
    quantity: int = Field(default=1, ge=1, le=20, description="Cantidad de pruebas")


class AssignedPathologistInfo(BaseModel):
    """Información del patólogo asignado al caso original."""
    id: str = Field(..., description="ID del patólogo")
    name: str = Field(..., description="Nombre completo del patólogo")


class ApprovalInfo(BaseModel):
    """Información del proceso de aprobación."""
    request_date: datetime = Field(default_factory=datetime.utcnow, description="Fecha de solicitud")
    reason: str = Field(..., max_length=1000, description="Motivo de la solicitud")
    assigned_pathologist: Optional[AssignedPathologistInfo] = Field(None, description="Información del patólogo del caso original")


class ApprovalRequest(BaseModel):
    """Modelo principal para solicitudes de aprobación."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    approval_code: str = Field(..., description="Código único de la solicitud (AP-YYYY-NNN)")
    original_case_code: str = Field(..., description="Código del caso original (YYYY-NNNNN)")
    approval_state: ApprovalStateEnum = Field(default=ApprovalStateEnum.REQUEST_MADE, description="Estado de la aprobación")
    complementary_tests: List[ComplementaryTestInfo] = Field(..., description="Pruebas complementarias solicitadas")
    approval_info: ApprovalInfo = Field(..., description="Información del proceso de aprobación")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('complementary_tests')
    @classmethod
    def validate_complementary_tests(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos una prueba complementaria')
        return v

    @field_validator('original_case_code')
    @classmethod
    def validate_original_case_code(cls, v):
        s = v.strip() if v else ''
        if not s:
            raise ValueError('El código del caso original es requerido')
        import re
        if not re.match(r'^20\d{2}-\d{5}$', s):
            raise ValueError('El código del caso original debe tener el formato YYYY-NNNNN (ejemplo: 2025-00001)')
        return s

    @field_validator('approval_code')
    @classmethod
    def validate_approval_code(cls, v):
        s = v.strip() if v else ''
        if not s:
            raise ValueError('El código de aprobación es requerido')
        import re
        if not re.match(r'^AP-20\d{2}-\d{3}$', s):
            raise ValueError('El código de aprobación debe tener el formato AP-YYYY-NNN (ejemplo: AP-2025-001)')
        return s

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str, datetime: lambda v: v.isoformat()}
        from_attributes = True
        allow_population_by_field_name = True
