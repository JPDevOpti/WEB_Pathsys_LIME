"""Modelo para Patólogo"""

from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument
# Importaciones simplificadas - ya no necesitamos los enums

class Patologo(BaseDocument):
    """Modelo de Patólogo para MongoDB"""
    patologoName: str = Field(..., min_length=2, max_length=200, description="Nombre completo del patólogo")
    InicialesPatologo: Optional[str] = Field(None, min_length=2, max_length=10, description="Iniciales del patólogo")
    patologoCode: str = Field(..., min_length=6, max_length=11, description="Cédula única del patólogo")
    PatologoEmail: EmailStr = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., min_length=5, max_length=50, description="Número de registro médico único")
    firma: str = Field(default="", description="URL de firma digital, por defecto vacío")
    observaciones: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "patologoName": "Dr. Juan Carlos Pérez González",
                "InicialesPatologo": "JCPG",
                "patologoCode": "123456",
                "PatologoEmail": "juan.perez@hospital.com",
                "registro_medico": "RM-12345",
                "isActive": True,
                "firma": "",
                "observaciones": "Especialista con 10 años de experiencia"
            }
        }