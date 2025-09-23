from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum


class EntidadInfo(BaseModel):
    id: str = Field(...)
    nombre: str = Field(...)

class Sexo(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class TipoAtencion(str, Enum):
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"


class PacienteBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=200)
    edad: int = Field(..., ge=0, le=150)
    sexo: Sexo = Field(...)
    entidad_info: EntidadInfo = Field(...)
    tipo_atencion: TipoAtencion = Field(...)
    observaciones: Optional[str] = Field(None, max_length=500)

    @validator('nombre', pre=True)
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre del paciente no puede estar vacío')
        return ' '.join(word.capitalize() for word in v.strip().split())

    class Config:
        populate_by_name = True
        use_enum_values = True


class PacienteCreate(PacienteBase):
    paciente_code: str = Field(...)
    
    @validator('paciente_code', pre=True)
    def validate_paciente_code(cls, v):
        if not v or not v.strip():
            raise ValueError('El código del paciente no puede estar vacío')
        codigo_clean = ''.join(c for c in v if c.isdigit())
        if not codigo_clean:
            raise ValueError('El código del paciente debe contener al menos un dígito')
        if len(codigo_clean) < 6 or len(codigo_clean) > 12:
            raise ValueError('El código del paciente debe tener entre 6 y 12 dígitos')
        return codigo_clean


class PacienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=200)
    edad: Optional[int] = Field(None, ge=0, le=150)
    sexo: Optional[Sexo] = None
    entidad_info: Optional[EntidadInfo] = None
    tipo_atencion: Optional[TipoAtencion] = None
    observaciones: Optional[str] = Field(None, max_length=500)

    @validator('nombre', pre=True)
    def validate_nombre(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre del paciente no puede estar vacío')
            return ' '.join(word.capitalize() for word in v.strip().split())
        return v

    class Config:
        use_enum_values = True


class PacienteResponse(PacienteBase):
    id: str = Field(...)
    paciente_code: str = Field(...)
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class PacienteSearch(BaseModel):
    nombre: Optional[str] = None
    paciente_code: Optional[str] = None
    edad_min: Optional[int] = Field(None, ge=0)
    edad_max: Optional[int] = Field(None, le=150)
    entidad: Optional[str] = None
    sexo: Optional[Sexo] = None
    tipo_atencion: Optional[TipoAtencion] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    class Config:
        use_enum_values = True

