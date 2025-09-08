"""Esquemas Pydantic para el módulo de aprobación"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.aprobacion.models.caso_aprobacion import (
    EstadoAprobacionEnum,
    PruebaComplementariaInfo,
    AprobacionInfo
)


class CasoAprobacionCreate(BaseModel):
    caso_original: str = Field(..., description="Código del caso original")
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias solicitadas")
    motivo: str = Field(..., max_length=1000, description="Motivo de la solicitud")


class CasoAprobacionUpdate(BaseModel):
    estado_aprobacion: Optional[EstadoAprobacionEnum] = None
    pruebas_complementarias: Optional[List[PruebaComplementariaInfo]] = None
    fecha_aprobacion: Optional[datetime] = None


class CasoAprobacionResponse(BaseModel):
    id: str = Field(..., description="ID único del caso de aprobación")
    caso_original: str = Field(..., description="Código del caso original")
    estado_aprobacion: EstadoAprobacionEnum = Field(..., description="Estado de aprobación")
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")

    class Config:
        from_attributes = True


class CasoAprobacionSearch(BaseModel):
    caso_original: Optional[str] = Field(None, description="Código del caso original")
    estado_aprobacion: Optional[EstadoAprobacionEnum] = None
    fecha_solicitud_desde: Optional[datetime] = None
    fecha_solicitud_hasta: Optional[datetime] = None
    fecha_aprobacion_desde: Optional[datetime] = None
    fecha_aprobacion_hasta: Optional[datetime] = None

    class Config:
        from_attributes = True


class CasoAprobacionStats(BaseModel):
    total_casos: int = 0
    casos_solicitud_hecha: int = 0
    casos_pendientes_aprobacion: int = 0
    casos_aprobados: int = 0
    casos_rechazados: int = 0

    class Config:
        from_attributes = True
