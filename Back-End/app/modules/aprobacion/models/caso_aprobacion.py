"""Modelo para casos de aprobación con pruebas complementarias."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.shared.models.base import PyObjectId


class EstadoAprobacionEnum(str, Enum):
    SOLICITUD_HECHA = "solicitud_hecha"
    PENDIENTE_APROBACION = "pendiente_aprobacion"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class PruebaComplementariaInfo(BaseModel):
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    cantidad: int = Field(default=1, ge=1, le=20, description="Cantidad de pruebas")


class PatologoAsignadoInfo(BaseModel):
    """Información del patólogo asignado al caso original"""
    codigo: str = Field(..., description="Código del patólogo")
    nombre: str = Field(..., description="Nombre completo del patólogo")
    firma: Optional[str] = Field(None, description="URL de la firma digital")

class AprobacionInfo(BaseModel):
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow, description="Fecha de solicitud")
    motivo: str = Field(..., max_length=1000, description="Motivo de la solicitud")
    patologo_asignado: Optional[PatologoAsignadoInfo] = Field(None, description="Información del patólogo del caso original")
    fecha_aprobacion: Optional[datetime] = Field(None, description="Fecha de aprobación/rechazo")
    fecha_gestion: Optional[datetime] = Field(None, description="Fecha en la que se marcó como pendiente de aprobación")


class CasoAprobacion(BaseModel):
    id: Optional[str] = Field(None, description="ID único del documento")
    caso_original: str = Field(..., description="Código del caso original (YYYY-NNNNN)")
    estado_aprobacion: EstadoAprobacionEnum = Field(default=EstadoAprobacionEnum.SOLICITUD_HECHA)
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias solicitadas")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso de aprobación")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

    @validator('pruebas_complementarias')
    def _validate_pruebas(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos una prueba complementaria')
        return v

    @validator('caso_original')
    def _validate_caso_original(cls, v):
        s = v.strip() if v else ''
        if not s:
            raise ValueError('El código del caso original es requerido')
        import re
        if not re.match(r'^20\d{2}-\d{5}$', s):
            raise ValueError('El código del caso original debe tener el formato YYYY-NNNNN (ejemplo: 2025-00001)')
        return s

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str, datetime: lambda v: v.isoformat()}
        from_attributes = True
        allow_population_by_field_name = True
