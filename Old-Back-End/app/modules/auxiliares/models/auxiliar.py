from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument

class Auxiliar(BaseDocument):
    """Modelo de Auxiliar"""
    
    auxiliar_name: str = Field(..., description="Nombre del auxiliar")
    auxiliar_code: str = Field(..., description="Código único del auxiliar")
    auxiliar_email: EmailStr = Field(..., description="Email del auxiliar")
    is_active: bool = Field(default=True, description="Estado activo del auxiliar")
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
                "auxiliar_name": "Ana María González",
                "auxiliar_code": "AUX001",
                "auxiliar_email": "ana.gonzalez@laboratorio.com",
                "is_active": True,
                "observaciones": "Auxiliar de laboratorio con experiencia en análisis clínicos"
            }
        }