"""Modelo para Pathologist"""

from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument

class Pathologist(BaseDocument):
    """Modelo de Pathologist para MongoDB"""
    pathologist_code: str = Field(..., max_length=11, description="Código único del patólogo")
    pathologist_name: str = Field(..., max_length=100, description="Nombre completo del patólogo")
    initials: Optional[str] = Field(None, max_length=10, description="Iniciales del patólogo")
    pathologist_email: EmailStr = Field(..., description="Email único del patólogo")
    medical_license: str = Field(..., max_length=50, description="Número de licencia médica única")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del patólogo")
    signature: str = Field(default="", description="URL de firma digital, por defecto vacío")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "pathologist_code": "123456",
                "pathologist_name": "Dr. Juan Carlos Pérez González",
                "initials": "JCPG",
                "pathologist_email": "juan.perez@hospital.com",
                "medical_license": "LM-12345",
                "is_active": True,
                "signature": "",
                "observations": "Especialista con 10 años de experiencia"
            }
        }
