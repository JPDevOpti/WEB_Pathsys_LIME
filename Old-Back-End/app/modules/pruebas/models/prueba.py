from pydantic import Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import BaseDocument, PyObjectId


class Prueba(BaseDocument):
    """Modelo de Prueba para la base de datos"""
    
    prueba_name: str = Field(..., description="Nombre de la prueba")
    prueba_code: str = Field(..., description="Código único de la prueba")
    prueba_description: Optional[str] = Field(None, description="Descripción de la prueba")
    tiempo: Optional[int] = Field(None, gt=0, description="Tiempo estimado en minutos")
    is_active: bool = Field(default=True, description="Estado activo de la prueba")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "prueba_name": "Hemoglobina",
                "prueba_code": "HB001",
                "prueba_description": "Análisis de hemoglobina en sangre",
                "tiempo": 30,
                "is_active": True
            }
        }