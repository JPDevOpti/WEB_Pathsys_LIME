"""Esquemas Pydantic para el módulo de aprobación"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.modules.aprobacion.models.caso_aprobacion import (
    EstadoAprobacionEnum,
    PruebaComplementariaInfo,
    PacienteInfo,
    MedicoInfo,
    PatologoInfo,
    MuestraInfo,
    ResultadoInfo,
    AprobacionInfo
)
from app.shared.schemas.common import EstadoCasoEnum


class CasoAprobacionCreate(BaseModel):
    """Modelo para crear un nuevo caso de aprobación"""
    caso_original: str = Field(..., description="Código del caso original")
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias solicitadas")
    motivo: str = Field(..., max_length=1000, description="Motivo de la solicitud")
    solicitado_por: str = Field(..., description="Usuario que solicita")


class CasoAprobacionUpdate(BaseModel):
    """Modelo para actualizar un caso de aprobación"""
    estado_aprobacion: Optional[EstadoAprobacionEnum] = None
    pruebas_complementarias: Optional[List[PruebaComplementariaInfo]] = None
    
    # Campos de gestión
    gestionado_por: Optional[str] = None
    fecha_gestion: Optional[datetime] = None
    comentarios_gestion: Optional[str] = Field(None, max_length=1000)
    
    # Campos de aprobación/rechazo
    aprobado_por: Optional[str] = None
    fecha_aprobacion: Optional[datetime] = None
    comentarios_aprobacion: Optional[str] = Field(None, max_length=1000)
    
    # Auditoría
    actualizado_por: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CasoAprobacionResponse(BaseModel):
    """Modelo de respuesta para casos de aprobación"""
    id: str = Field(..., description="ID único del caso de aprobación")
    caso_aprobacion: str = Field(..., description="Código único del caso de aprobación")
    caso_original: str = Field(..., description="Código del caso original")
    
    # Información del caso
    paciente: PacienteInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[MedicoInfo] = None
    servicio: Optional[str] = None
    muestras: List[MuestraInfo] = Field(..., description="Muestras del caso")
    estado_caso_original: EstadoCasoEnum = Field(..., description="Estado del caso original")
    patologo_asignado: Optional[PatologoInfo] = None
    resultado: Optional[ResultadoInfo] = None
    
    # Información de aprobación
    estado_aprobacion: EstadoAprobacionEnum = Field(..., description="Estado de aprobación")
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso")
    
    # Auditoría
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de actualización")
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True


class CasoAprobacionSearch(BaseModel):
    """Modelo para búsqueda de casos de aprobación"""
    query: Optional[str] = Field(None, description="Búsqueda general")
    caso_code: Optional[str] = Field(None, description="Código del caso original")
    caso_aprobacion: Optional[str] = Field(None, description="Código del caso de aprobación")
    paciente_code: Optional[str] = Field(None, description="Código del paciente")
    paciente_nombre: Optional[str] = Field(None, description="Nombre del paciente")
    estado_aprobacion: Optional[EstadoAprobacionEnum] = None
    solicitado_por: Optional[str] = Field(None, description="Usuario solicitante")
    aprobado_por: Optional[str] = Field(None, description="Usuario aprobador")
    fecha_solicitud_desde: Optional[datetime] = None
    fecha_solicitud_hasta: Optional[datetime] = None
    fecha_aprobacion_desde: Optional[datetime] = None
    fecha_aprobacion_hasta: Optional[datetime] = None
    incluir_inactivos: bool = Field(default=False, description="Incluir registros inactivos")

    class Config:
        from_attributes = True


class CasoAprobacionStats(BaseModel):
    """Estadísticas de casos de aprobación"""
    total_casos: int = 0
    casos_pendientes: int = 0
    casos_gestionando: int = 0
    casos_aprobados: int = 0
    casos_rechazados: int = 0
    
    # Estadísticas de tiempo
    tiempo_promedio_aprobacion: Optional[float] = Field(None, description="Días promedio de aprobación")
    tiempo_promedio_gestion: Optional[float] = Field(None, description="Días promedio de gestión")
    
    # Por solicitante
    casos_por_solicitante: Dict[str, int] = Field(default_factory=dict)
    
    # Por aprobador
    casos_por_aprobador: Dict[str, int] = Field(default_factory=dict)
    
    # Por tipo de prueba
    pruebas_mas_solicitadas: Dict[str, int] = Field(default_factory=dict)
    
    # Tendencias mensuales
    casos_mes_actual: int = 0
    casos_mes_anterior: int = 0
    cambio_porcentual: float = 0.0

    class Config:
        from_attributes = True
