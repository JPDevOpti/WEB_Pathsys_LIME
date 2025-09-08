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


class AprobacionInfo(BaseModel):
    solicitado_por: str = Field(..., description="Usuario que solicita la aprobación")
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow, description="Fecha de solicitud")
    motivo: str = Field(..., max_length=1000, description="Motivo de la solicitud")
    aprobado_por: Optional[str] = Field(None, description="Usuario que aprueba/rechaza")
    fecha_aprobacion: Optional[datetime] = Field(None, description="Fecha de aprobación/rechazo")
    comentarios_aprobacion: Optional[str] = Field(None, max_length=1000, description="Comentarios del aprobador")
    gestionado_por: Optional[str] = Field(None, description="Usuario que gestiona el caso")
    fecha_gestion: Optional[datetime] = Field(None, description="Fecha de inicio de gestión")
    comentarios_gestion: Optional[str] = Field(None, max_length=1000, description="Comentarios de gestión")


class CasoAprobacion(BaseModel):
    caso_original: str = Field(..., description="Código del caso original (YYYY-NNNNN)")
    estado_aprobacion: EstadoAprobacionEnum = Field(default=EstadoAprobacionEnum.SOLICITUD_HECHA)
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias solicitadas")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso de aprobación")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

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
