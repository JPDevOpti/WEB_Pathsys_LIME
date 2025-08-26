from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument

class Residente(BaseDocument):
    """Modelo de Residente"""
    
    residenteName: str = Field(..., description="Nombre del residente")
    InicialesResidente: Optional[str] = Field(default="", description="Iniciales del residente")
    residenteCode: str = Field(..., description="Código único del residente")
    ResidenteEmail: str = Field(..., description="Email del residente")
    registro_medico: str = Field(..., description="Número de registro médico")
    observaciones: Optional[str] = Field(default="", description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "residenteName": "Dr. María Elena Rodríguez López",
                "InicialesResidente": "MERL",
                "residenteCode": "12345678",
                "ResidenteEmail": "maria.rodriguez@hospital.com",
                "registro_medico": "RM-2024-001",
                "observaciones": "Residente de segundo año en patología"
            }
        }