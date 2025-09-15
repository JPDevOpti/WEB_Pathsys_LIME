from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UrgentCasesRequest(BaseModel):
    """Solicitud de casos urgentes"""
    patologo_codigo: Optional[str] = None
    estado: Optional[str] = None
    limite: int = Field(50, ge=1, le=200)


class UrgentCaseRow(BaseModel):
    """Fila de caso urgente"""
    caso_code: str
    paciente_nombre: str
    paciente_documento: Optional[str] = None
    fecha_creacion: datetime
    dias_habiles_transcurridos: int
    estado: str
    prioridad: str
    patologo_nombre: Optional[str] = None
    medico_solicitante: Optional[str] = None
    entidad_nombre: Optional[str] = None
    pruebas: List[str] = []


class UrgentCasesResponse(BaseModel):
    """Respuesta de casos urgentes"""
    casos: List[UrgentCaseRow]
    total: int
    limite_aplicado: int