from typing import Optional
from pydantic import Field, EmailStr
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument

class Facturacion(BaseDocument):
    """Modelo de Facturación"""
    
    facturacion_name: str = Field(..., description="Nombre del usuario de facturación")
    facturacion_code: str = Field(..., description="Código único del usuario de facturación")
    facturacion_email: EmailStr = Field(..., description="Email del usuario de facturación")
    is_active: bool = Field(default=True, description="Estado activo del usuario de facturación")
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
                "facturacion_name": "Ana María González",
                "facturacion_code": "FAC001",
                "facturacion_email": "ana.gonzalez@facturacion.com",
                "is_active": True,
                "observaciones": "Usuario de facturación con experiencia en contabilidad"
            }
        }
