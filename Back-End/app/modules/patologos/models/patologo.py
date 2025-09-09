"""Modelo para Patólogo"""

from typing import Optional
from pydantic import Field
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument
# Importaciones simplificadas - ya no necesitamos los enums

class Patologo(BaseDocument):
    """Modelo de Patólogo para MongoDB"""
    patologo_name: str = Field(..., max_length=100, description="Nombre completo del patólogo")
    iniciales_patologo: Optional[str] = Field(None, max_length=10, description="Iniciales del patólogo")
    patologo_code: str = Field(..., max_length=11, description="Código único del patólogo (identificador principal)")
    patologo_email: str = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., max_length=50, description="Número de registro médico único")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del patólogo")
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
                "patologo_name": "Dr. Juan Carlos Pérez González",
                "iniciales_patologo": "JCPG",
                "patologo_code": "123456",
                "patologo_email": "juan.perez@hospital.com",
                "registro_medico": "RM-12345",
                "is_active": True,
                "firma": "",
                "observaciones": "Especialista con 10 años de experiencia"
            }
        }