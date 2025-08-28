"""Modelo para Paciente"""

from typing import Optional, List
from pydantic import Field
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument
from app.modules.pacientes.schemas.paciente import Sexo

class Paciente(BaseDocument):
    """Modelo de Paciente para MongoDB"""
    paciente_code: str = Field(..., min_length=6, max_length=12, description="Código único del paciente (identificador principal)")
    nombre: str = Field(..., min_length=2, max_length=200, description="Nombre completo del paciente")
    edad: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sexo: Sexo = Field(..., description="Sexo del paciente (Masculino/Femenino)")
    entidad_info: dict = Field(..., description="Información de la entidad de salud")
    tipo_atencion: str = Field(..., description="Tipo de atención: Ambulatorio u Hospitalizado")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    id_casos: List[str] = Field(default_factory=list, description="IDs de casos asociados")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "paciente_code": "12345678",
                "nombre": "Juan Carlos Pérez",
                "edad": 35,
                "sexo": "Masculino",
                "entidad_info": {
                    "id": "ent_001",
                    "nombre": "EPS Sanitas"
                },
                "tipo_atencion": "Ambulatorio",
                "observaciones": "Paciente con antecedentes de hipertensión",
                "id_casos": [],
                "fecha_creacion": "2024-01-15T10:30:00Z",
                "fecha_actualizacion": "2024-01-15T10:30:00Z"
            }
        }