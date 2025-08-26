from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId
from typing import Optional

from app.shared.models.base import BaseDocument

class Auxiliar(BaseDocument):
    """Modelo de Auxiliar"""
    
    auxiliarName: str = Field(..., description="Nombre del auxiliar")
    auxiliarCode: str = Field(..., description="Código único del auxiliar")
    AuxiliarEmail: EmailStr = Field(..., description="Email del auxiliar")
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
                "auxiliarName": "Ana María González",
                "auxiliarCode": "AUX001",
                "AuxiliarEmail": "ana.gonzalez@laboratorio.com",
                "observaciones": "Auxiliar de laboratorio con experiencia en análisis clínicos"
            }
        }