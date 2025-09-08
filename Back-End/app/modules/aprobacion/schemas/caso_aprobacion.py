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
    gestionado_por: Optional[str] = None
    fecha_gestion: Optional[datetime] = None
    comentarios_gestion: Optional[str] = Field(None, max_length=1000)
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    comentarios_aprobacion: Optional[str] = Field(None, max_length=1000)
    actualizado_por: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CasoAprobacionResponse(BaseModel):
    id: str = Field(..., description="ID único del caso de aprobación")
    caso_original: str = Field(..., description="Código del caso original")
    estado_aprobacion: EstadoAprobacionEnum = Field(..., description="Estado de aprobación")
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de actualización")
    creado_por: Optional[str] = None

    class Config:
        from_attributes = True


class CasoAprobacionSearch(BaseModel):
    caso_original: Optional[str] = Field(None, description="Código del caso original")
    estado_aprobacion: Optional[EstadoAprobacionEnum] = None
    solicitado_por: Optional[str] = Field(None, description="Usuario solicitante")
    aprobado_por: Optional[str] = Field(None, description="Usuario aprobador")
    fecha_solicitud_desde: Optional[datetime] = None
    fecha_solicitud_hasta: Optional[datetime] = None
    fecha_aprobacion_desde: Optional[datetime] = None
    fecha_aprobacion_hasta: Optional[datetime] = None

    class Config:
        from_attributes = True


class CasoAprobacionStats(BaseModel):
    total_casos: int = 0
    casos_pendientes: int = 0
    casos_gestionando: int = 0
    casos_aprobados: int = 0
    casos_rechazados: int = 0

    class Config:
        from_attributes = True
