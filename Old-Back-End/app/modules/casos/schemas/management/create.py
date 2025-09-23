from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class PatientSex(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"


class AttentionType(str, Enum):
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"


class CasePriority(str, Enum):
    NORMAL = "Normal"
    PRIORITARIO = "Prioritario"


class CaseState(str, Enum):
    EN_PROCESO = "En proceso"
    POR_FIRMAR = "Por firmar"
    POR_ENTREGAR = "Por entregar"
    COMPLETADO = "Completado"


class EntityInfo(BaseModel):
    id: str = Field(..., description="Código de la entidad")
    nombre: str = Field(..., description="Nombre de la entidad")


class PatientInfo(BaseModel):
    paciente_code: str = Field(..., description="Código del paciente")
    nombre: str = Field(..., description="Nombre completo del paciente")
    edad: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sexo: PatientSex = Field(..., description="Sexo del paciente")
    entidad_info: EntityInfo = Field(..., description="Información de la entidad")
    tipo_atencion: AttentionType = Field(..., description="Tipo de atención")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones del paciente")


class SubsampleTest(BaseModel):
    id: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    cantidad: int = Field(..., ge=1, le=10, description="Cantidad de pruebas")


class Subsample(BaseModel):
    region_cuerpo: str = Field(..., min_length=1, max_length=100, description="Región del cuerpo")
    pruebas: List[SubsampleTest] = Field(..., min_items=1, description="Lista de pruebas a realizar")
    
    @validator('pruebas')
    def validate_pruebas_not_empty(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos una prueba')
        return v


class CreateCaseRequest(BaseModel):
    paciente: PatientInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico solicitante")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico")
    muestras: List[Subsample] = Field(..., min_items=1, description="Lista de submuestras")
    estado: CaseState = Field(default=CaseState.EN_PROCESO, description="Estado inicial del caso")
    prioridad: CasePriority = Field(default=CasePriority.NORMAL, description="Prioridad del caso")
    observaciones_generales: Optional[str] = Field(None, max_length=500, description="Observaciones generales del caso")
    
    @validator('muestras')
    def validate_muestras_not_empty(cls, v):
        if not v:
            raise ValueError('Debe especificar al menos una muestra')
        return v


class CreatedCaseInfo(BaseModel):
    id: str = Field(..., description="ID del caso")
    caso_code: str = Field(..., description="Código del caso")
    paciente: PatientInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, description="Médico solicitante")
    servicio: Optional[str] = Field(None, description="Servicio médico")
    muestras: List[Subsample] = Field(..., description="Lista de submuestras")
    estado: CaseState = Field(..., description="Estado del caso")
    prioridad: CasePriority = Field(..., description="Prioridad del caso")
    observaciones_generales: Optional[str] = Field(None, description="Observaciones generales")
    fecha_creacion: datetime = Field(..., description="Fecha de creación del caso")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")


class CreateCaseResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    caso_code: str = Field(..., description="Código del caso creado")
    case: CreatedCaseInfo = Field(..., description="Información del caso creado")
