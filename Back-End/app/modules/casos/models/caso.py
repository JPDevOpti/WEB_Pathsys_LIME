"""Modelos Pydantic para el manejo de casos médicos en MongoDB."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.shared.models.base import PyObjectId
from app.shared.schemas.common import EstadoCasoEnum
from app.modules.pruebas.schemas.prueba import PruebasItem


class EntidadInfo(BaseModel):
    """Información de la entidad de salud."""
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)


class MuestraInfo(BaseModel):
    """Información de una muestra dentro de un caso."""
    region_cuerpo: str = Field(...)
    pruebas: List[PruebasItem] = Field(default_factory=list)


class PacienteInfo(BaseModel):
    """Información del paciente en un caso."""
    codigo: str = Field(..., max_length=50)
    cedula: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=200)
    edad: int = Field(..., ge=0, le=150)
    sexo: str = Field(..., max_length=20)
    entidad_info: EntidadInfo
    tipo_atencion: str = Field(..., max_length=50)
    observaciones: Optional[str] = Field(None, max_length=1000)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

    @validator('edad')
    def validate_edad(cls, v):
        if v < 0 or v > 150:
            raise ValueError('La edad debe estar entre 0 y 150 años')
        return v


class MedicoInfo(BaseModel):
    """Información del médico solicitante."""
    nombre: str = Field(..., max_length=200)


class PatologoInfo(BaseModel):
    """Información del patólogo asignado."""
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)


class TipoResultadoEnum(str, Enum):
    """Tipos de resultado disponibles."""
    HISTOPATOLOGIA = "histopatologia"
    CITOLOGIA = "citologia"
    INMUNOHISTOQUIMICA = "inmunohistoquimica"


class DiagnosticoCIE10(BaseModel):
    """Información del diagnóstico CIE-10."""
    id: str = Field(..., description="ID único de la enfermedad CIE-10")
    codigo: str = Field(..., max_length=20, description="Código CIE-10 de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIE-10")


class DiagnosticoCIEO(BaseModel):
    """Información del diagnóstico CIEO (cáncer)."""
    id: str = Field(..., description="ID único de la enfermedad CIEO")
    codigo: str = Field(..., max_length=20, description="Código CIEO de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIEO")


class ResultadoInfo(BaseModel):
    """Información de resultados del caso."""
    tipo_resultado: Optional[TipoResultadoEnum] = None
    metodo: Optional[str] = None
    resultado_macro: Optional[str] = None
    resultado_micro: Optional[str] = None
    diagnostico: Optional[str] = None
    diagnostico_cie10: Optional[DiagnosticoCIE10] = None
    diagnostico_cieo: Optional[DiagnosticoCIEO] = None
    observaciones: Optional[str] = None
    fecha_resultado: Optional[datetime] = None
    firmado: bool = Field(default=False)
    fecha_firma: Optional[datetime] = None

class Caso(BaseModel):
    """Modelo principal de Caso para MongoDB."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    caso_code: str = Field(..., max_length=50)
    paciente: PacienteInfo
    medico_solicitante: Optional[MedicoInfo] = None
    servicio: Optional[str] = Field(None, max_length=100)
    muestras: List[MuestraInfo] = Field(min_items=1)
    estado: EstadoCasoEnum = Field(default=EstadoCasoEnum.EN_PROCESO)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_firma: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    patologo_asignado: Optional[PatologoInfo] = None
    resultado: Optional[ResultadoInfo] = None
    observaciones_generales: Optional[str] = Field(None, max_length=1000)
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None
    activo: bool = Field(default=True)

    @validator('muestras')
    def validate_muestras(cls, v):
        if not v:
            raise ValueError('Debe existir al menos una muestra')
        return v

    @validator('fecha_firma')
    def validate_fecha_firma(cls, v, values):
        if v and 'fecha_creacion' in values:
            if v < values['fecha_creacion']:
                raise ValueError('La fecha de firma no puede ser anterior a la fecha de creación')
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True
