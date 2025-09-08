"""Modelo para casos de aprobación con pruebas complementarias."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.shared.models.base import PyObjectId
from app.shared.schemas.common import EstadoCasoEnum
from app.modules.pruebas.schemas.prueba import PruebasItem
from app.modules.casos.models.caso import PrioridadCasoEnum


class EstadoAprobacionEnum(str, Enum):
    """Estados específicos del proceso de aprobación."""
    PENDIENTE = "pendiente"
    GESTIONANDO = "gestionando"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"


class PruebaComplementariaInfo(BaseModel):
    """Información de una prueba complementaria."""
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    cantidad: int = Field(default=1, ge=1, le=20, description="Cantidad de pruebas")
    costo: Optional[float] = Field(None, ge=0, description="Costo de la prueba")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones de la prueba")


class EntidadInfo(BaseModel):
    """Información de la entidad de salud."""
    id: str = Field(..., max_length=50, description="ID único de la entidad")
    nombre: str = Field(..., max_length=200, description="Nombre de la entidad")


class MuestraInfo(BaseModel):
    """Información de una muestra dentro de un caso."""
    region_cuerpo: str = Field(..., description="Región del cuerpo de donde se tomó la muestra")
    pruebas: List[PruebasItem] = Field(default_factory=list, description="Lista de pruebas a realizar")


class PacienteInfo(BaseModel):
    """Información del paciente en un caso de aprobación."""
    paciente_code: str = Field(..., max_length=50, description="Código único del paciente")
    nombre: str = Field(..., max_length=200, description="Nombre completo del paciente")
    edad: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sexo: str = Field(..., max_length=20, description="Sexo del paciente")
    entidad_info: EntidadInfo = Field(..., description="Información de la entidad de salud")
    tipo_atencion: str = Field(..., max_length=50, description="Tipo de atención")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones del paciente")


class PatologoInfo(BaseModel):
    """Información del patólogo asignado."""
    codigo: str = Field(..., description="Código único del patólogo")
    nombre: str = Field(..., description="Nombre completo del patólogo")
    firma: Optional[str] = Field(None, description="Firma digital del patólogo")


class DiagnosticoCIE10(BaseModel):
    """Información del diagnóstico CIE-10."""
    codigo: str = Field(..., max_length=20, description="Código CIE-10 de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIE-10")


class DiagnosticoCIEO(BaseModel):
    """Información del diagnóstico CIEO (cáncer)."""
    codigo: str = Field(..., max_length=20, description="Código CIEO de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIEO")


class ResultadoInfo(BaseModel):
    """Información de resultados del caso."""
    metodo: Optional[List[str]] = Field(default_factory=list, description="Lista de métodos utilizados")
    resultado_macro: Optional[str] = Field(None, description="Descripción macroscópica")
    resultado_micro: Optional[str] = Field(None, description="Descripción microscópica")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico final")
    diagnostico_cie10: Optional[DiagnosticoCIE10] = Field(None, description="Diagnóstico CIE-10")
    diagnostico_cieo: Optional[DiagnosticoCIEO] = Field(None, description="Diagnóstico CIEO (cáncer)")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    fecha_resultado: Optional[datetime] = Field(None, description="Fecha del resultado")
    firmado: bool = Field(default=False, description="Si el resultado está firmado")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma")


class AprobacionInfo(BaseModel):
    """Información del proceso de aprobación."""
    solicitado_por: str = Field(..., description="Usuario que solicita la aprobación")
    fecha_solicitud: datetime = Field(default_factory=datetime.utcnow, description="Fecha de solicitud")
    motivo: str = Field(..., max_length=1000, description="Motivo de la solicitud de aprobación")
    
    # Información del aprobador
    aprobado_por: Optional[str] = Field(None, description="Usuario que aprueba/rechaza")
    fecha_aprobacion: Optional[datetime] = Field(None, description="Fecha de aprobación/rechazo")
    comentarios_aprobacion: Optional[str] = Field(None, max_length=1000, description="Comentarios del aprobador")
    
    # Gestión intermedia
    gestionado_por: Optional[str] = Field(None, description="Usuario que gestiona el caso")
    fecha_gestion: Optional[datetime] = Field(None, description="Fecha de inicio de gestión")
    comentarios_gestion: Optional[str] = Field(None, max_length=1000, description="Comentarios de gestión")


class CasoAprobacion(BaseModel):
    """Modelo principal de Caso de Aprobación para MongoDB."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    caso_original: str = Field(..., description="Código del caso original")
    caso_aprobacion: str = Field(..., max_length=50, description="Código único del caso de aprobación")
    
    # Información copiada del caso original
    paciente: PacienteInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico que solicita")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico")
    muestras: List[MuestraInfo] = Field(..., description="Muestras del caso")
    estado_caso_original: EstadoCasoEnum = Field(..., description="Estado del caso original")
    prioridad: PrioridadCasoEnum = Field(default=PrioridadCasoEnum.NORMAL, description="Prioridad del caso")
    patologo_asignado: Optional[PatologoInfo] = Field(None, description="Patólogo asignado")
    resultado: Optional[ResultadoInfo] = Field(None, description="Resultado del caso")
    
    # Información específica de aprobación
    estado_aprobacion: EstadoAprobacionEnum = Field(default=EstadoAprobacionEnum.PENDIENTE)
    pruebas_complementarias: List[PruebaComplementariaInfo] = Field(..., description="Pruebas complementarias solicitadas")
    aprobacion_info: AprobacionInfo = Field(..., description="Información del proceso de aprobación")
    
    # Campos de auditoría
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación")
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    creado_por: Optional[str] = Field(None, description="Usuario que creó el registro")
    actualizado_por: Optional[str] = Field(None, description="Usuario que actualizó el registro")
    is_active: bool = Field(default=True, description="Si el registro está activo")
    
    @validator('pruebas_complementarias')
    def validate_pruebas_complementarias(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe especificar al menos una prueba complementaria')
        return v
    
    @validator('caso_aprobacion')
    def validate_caso_aprobacion(cls, v):
        if not v or not v.strip():
            raise ValueError('El código del caso de aprobación es requerido')
        
        caso_code = v.strip()
        
        # Validar formato A-YYYY-NNNNN
        import re
        pattern = r'^A-20\d{2}-\d{5}$'
        if not re.match(pattern, caso_code):
            raise ValueError('El código del caso de aprobación debe tener el formato A-YYYY-NNNNN (ejemplo: A-2025-00001)')
        
        return caso_code
    
    @validator('caso_original')
    def validate_caso_original(cls, v):
        if not v or not v.strip():
            raise ValueError('El código del caso original es requerido')
        
        caso_code = v.strip()
        
        # Validar formato YYYY-NNNNN
        import re
        pattern = r'^20\d{2}-\d{5}$'
        if not re.match(pattern, caso_code):
            raise ValueError('El código del caso original debe tener el formato YYYY-NNNNN (ejemplo: 2025-00001)')
        
        return caso_code

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True
