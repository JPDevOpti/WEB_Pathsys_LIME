from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument

class Residente(BaseDocument):
    """Modelo de Residente"""
    
    residente_name: str = Field(..., description="Nombre del residente")
    iniciales_residente: Optional[str] = Field(default="", description="Iniciales del residente")
    residente_code: str = Field(..., description="Código único del residente")
    residente_email: str = Field(..., description="Email del residente")
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
                "residente_name": "Dr. María Elena Rodríguez López",
                "iniciales_residente": "MERL",
                "residente_code": "12345678",
                "residente_email": "maria.rodriguez@hospital.com",
                "registro_medico": "RM-2024-001",
                "observaciones": "Residente de segundo año en patología"
            }
        }