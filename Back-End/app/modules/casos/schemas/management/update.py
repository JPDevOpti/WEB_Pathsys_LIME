from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from .create import PatientSex, AttentionType, CasePriority, CaseState, EntityInfo, PatientInfo, SubsampleTest, Subsample


class PatologoInfo(BaseModel):
    """Información del patólogo asignado."""
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=200)
    firma: Optional[str] = Field(None, description="Firma digital del patólogo")


class DiagnosticoCIE10(BaseModel):
    """Información del diagnóstico CIE-10."""
    codigo: str = Field(..., max_length=20, description="Código CIE-10 de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIE-10")


class DiagnosticoCIEO(BaseModel):
    """Información del diagnóstico CIEO (cáncer)."""
    codigo: str = Field(..., max_length=20, description="Código CIEO de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIEO")


class NotaAdicional(BaseModel):
    """Información de una nota adicional agregada al caso."""
    fecha: datetime = Field(default_factory=datetime.utcnow, description="Fecha y hora de la nota")
    nota: str = Field(..., max_length=1000, description="Contenido de la nota adicional")
    agregado_por: Optional[str] = Field(None, max_length=100, description="Usuario que agregó la nota")


class ResultadoInfo(BaseModel):
    """Información de resultados del caso."""
    metodo: Optional[List[str]] = Field(default_factory=list, description="Lista de métodos utilizados")
    resultado_macro: Optional[str] = None
    resultado_micro: Optional[str] = None
    diagnostico: Optional[str] = None
    diagnostico_cie10: Optional[DiagnosticoCIE10] = None
    diagnostico_cieo: Optional[DiagnosticoCIEO] = None
    observaciones: Optional[str] = None


class UpdateCaseRequest(BaseModel):
    """Solicitud para actualizar un caso existente - TODOS los campos posibles"""
    
    # Campos básicos del caso
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico solicitante")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico")
    muestras: Optional[List[Subsample]] = Field(None, description="Lista de submuestras")
    estado: Optional[CaseState] = Field(None, description="Estado del caso")
    prioridad: Optional[CasePriority] = Field(None, description="Prioridad del caso")
    observaciones_generales: Optional[str] = Field(None, max_length=1000, description="Observaciones generales del caso")
    entregado_a: Optional[str] = Field(None, max_length=100, description="Persona que recibe el caso al ser entregado")
    oportunidad: Optional[int] = Field(None, ge=0, description="Días hábiles transcurridos al completar el caso")
    
    # Información del paciente (opcional para actualización)
    paciente: Optional[PatientInfo] = Field(None, description="Información del paciente")
    
    # Patólogo asignado
    patologo_asignado: Optional[PatologoInfo] = Field(None, description="Patólogo asignado al caso")
    
    # Resultados del caso
    resultado: Optional[ResultadoInfo] = Field(None, description="Resultados del caso")
    
    # Notas adicionales
    notas_adicionales: Optional[List[NotaAdicional]] = Field(None, description="Notas adicionales del caso")
    
    # Fechas específicas (solo si se necesita actualizar manualmente)
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma del caso")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega del caso")
    
    @validator('muestras')
    def validate_muestras_not_empty(cls, v):
        if v is not None and not v:
            raise ValueError('Si se especifican muestras, debe haber al menos una')
        return v
    
    @validator('fecha_firma')
    def validate_fecha_firma(cls, v, values):
        if v and 'fecha_creacion' in values:
            if v < values['fecha_creacion']:
                raise ValueError('La fecha de firma no puede ser anterior a la fecha de creación')
        return v


class UpdatedCaseInfo(BaseModel):
    """Información del caso actualizado - TODOS los campos posibles"""
    id: str = Field(..., description="ID del caso")
    caso_code: str = Field(..., description="Código del caso")
    paciente: PatientInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, description="Médico solicitante")
    servicio: Optional[str] = Field(None, description="Servicio médico")
    muestras: List[Subsample] = Field(..., description="Lista de submuestras")
    estado: CaseState = Field(..., description="Estado del caso")
    prioridad: CasePriority = Field(..., description="Prioridad del caso")
    observaciones_generales: Optional[str] = Field(None, description="Observaciones generales")
    entregado_a: Optional[str] = Field(None, description="Persona que recibe el caso al ser entregado")
    oportunidad: Optional[int] = Field(None, description="Días hábiles transcurridos al completar el caso")
    
    # Patólogo asignado
    patologo_asignado: Optional[PatologoInfo] = Field(None, description="Patólogo asignado al caso")
    
    # Resultados del caso
    resultado: Optional[ResultadoInfo] = Field(None, description="Resultados del caso")
    
    # Notas adicionales
    notas_adicionales: Optional[List[NotaAdicional]] = Field(None, description="Notas adicionales del caso")
    
    # Fechas
    fecha_creacion: datetime = Field(..., description="Fecha de creación del caso")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma del caso")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega del caso")
    
    # Campos de auditoría
    ingresado_por: Optional[str] = Field(None, description="Usuario que ingresó el caso")
    actualizado_por: Optional[str] = Field(None, description="Usuario que actualizó el caso")


class UpdateCaseResponse(BaseModel):
    """Respuesta de actualización de caso"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje de respuesta")
    caso_code: str = Field(..., description="Código del caso actualizado")
    case: UpdatedCaseInfo = Field(..., description="Información del caso actualizado")
