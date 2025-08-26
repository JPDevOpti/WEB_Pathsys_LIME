"""Esquemas para el módulo de pacientes"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum


class EntidadInfo(BaseModel):
    """Información de la entidad de salud"""
    id: str = Field(..., description="ID único de la entidad")
    nombre: str = Field(..., description="Nombre de la entidad de salud")

    class Config:
        populate_by_name = True


class Sexo(str, Enum):
    """Enumeración para el sexo del paciente"""
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"


class TipoAtencion(str, Enum):
    """Enumeración para el tipo de atención"""
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"


class PacienteBase(BaseModel):
    """Esquema base para pacientes"""
    nombre: str = Field(
        ..., 
        min_length=2, 
        max_length=200, 
        description="Nombre completo del paciente"
    )
    edad: int = Field(
        ..., 
        ge=0, 
        le=150, 
        description="Edad del paciente"
    )
    sexo: Sexo = Field(
        ..., 
        description="Sexo del paciente (Masculino/Femenino)"
    )
    entidad_info: EntidadInfo = Field(
        ..., 
        description="Información de la entidad de salud a la que está afiliado el paciente"
    )
    tipo_atencion: TipoAtencion = Field(
        ..., 
        description="Tipo de atención: Ambulatorio u Hospitalizado"
    )
    observaciones: Optional[str] = Field(
        None, 
        max_length=500,
        description="Observaciones adicionales sobre el paciente"
    )

    @validator('nombre', pre=True)
    def validate_nombre(cls, v):
        """Validar y normalizar nombre del paciente"""
        if not v or not v.strip():
            raise ValueError('El nombre del paciente no puede estar vacío')
        # Capitalizar cada palabra del nombre
        return ' '.join(word.capitalize() for word in v.strip().split())

    class Config:
        populate_by_name = True
        use_enum_values = True


class PacienteCreate(PacienteBase):
    """Esquema para crear un paciente"""
    cedula: str = Field(
        ..., 
        description="Número de cédula del paciente (será usado como ID único)"
    )
    
    @validator('cedula', pre=True)
    def validate_cedula(cls, v):
        """Validar número de cédula"""
        if not v or not v.strip():
            raise ValueError('La cédula no puede estar vacía')
        # Remover espacios y caracteres no numéricos
        cedula_clean = ''.join(c for c in v if c.isdigit())
        if not cedula_clean:
            raise ValueError('La cédula debe contener al menos un dígito')
        if len(cedula_clean) < 6 or len(cedula_clean) > 12:
            raise ValueError('La cédula debe tener entre 6 y 12 dígitos')
        return cedula_clean


class PacienteUpdate(BaseModel):
    """Esquema para actualizar un paciente"""
    nombre: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=200
    )
    edad: Optional[int] = Field(None, ge=0, le=150)
    sexo: Optional[Sexo] = None
    entidad_info: Optional[EntidadInfo] = Field(None, description="Información de la entidad de salud")
    tipo_atencion: Optional[TipoAtencion] = None
    observaciones: Optional[str] = Field(None, max_length=500)

    @validator('nombre', pre=True)
    def validate_nombre(cls, v):
        """Validar nombre en actualización"""
        if v is not None:
            if not v.strip():
                raise ValueError('El nombre del paciente no puede estar vacío')
            return ' '.join(word.capitalize() for word in v.strip().split())
        return v

    class Config:
        use_enum_values = True


class PacienteResponse(PacienteBase):
    """Esquema de respuesta para un paciente"""
    id: str = Field(..., description="ID único del paciente (cédula)")
    cedula: str = Field(
        ..., 
        description="Número de cédula del paciente"
    )
    fecha_creacion: Optional[datetime] = Field(
        None,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: Optional[datetime] = Field(
        None,
        description="Fecha de última actualización"
    )
    id_casos: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de IDs de casos asociados al paciente"
    )

    class Config:
        from_attributes = True
        use_enum_values = True


class PacienteSearch(BaseModel):
    """Esquema para búsqueda de pacientes"""
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    edad_min: Optional[int] = Field(None, ge=0)
    edad_max: Optional[int] = Field(None, le=150)
    entidad: Optional[str] = None  # Nombre de la entidad para filtrar
    sexo: Optional[Sexo] = None
    tipo_atencion: Optional[TipoAtencion] = None
    tiene_casos: Optional[bool] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    class Config:
        use_enum_values = True


class PacienteStats(BaseModel):
    """Esquema para estadísticas de pacientes"""
    total_pacientes: int = Field(..., description="Total de pacientes registrados")
    total_hombres: int = Field(..., description="Total de pacientes hombres")
    total_mujeres: int = Field(..., description="Total de pacientes mujeres")
    promedio_edad: float = Field(..., description="Edad promedio de los pacientes")
    edad_min: int = Field(..., description="Edad mínima registrada")
    edad_max: int = Field(..., description="Edad máxima registrada")
    total_ambulatorios: int = Field(..., description="Total de pacientes ambulatorios")
    total_hospitalizados: int = Field(..., description="Total de pacientes hospitalizados")
    entidades_mas_frecuentes: List[dict] = Field(..., description="Entidades con más pacientes")
    pacientes_con_casos: int = Field(..., description="Pacientes que tienen casos asociados")
    
    # Estadísticas mensuales para el dashboard
    pacientes_mes_actual: int = Field(0, description="Pacientes registrados este mes")
    pacientes_mes_anterior: int = Field(0, description="Pacientes registrados el mes anterior")
    cambio_porcentual: float = Field(0.0, description="Cambio porcentual respecto al mes anterior")
    
    # Distribución por género para el dashboard
    distribucion_genero: Dict[str, int] = Field(default_factory=dict, description="Distribución por género")
    
    class Config:
        from_attributes = True