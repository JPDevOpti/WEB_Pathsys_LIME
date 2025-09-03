from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import PyObjectId


class PruebaCreate(BaseModel):
    """Esquema para crear una nueva prueba"""
    prueba_name: str = Field(..., max_length=200, description="Nombre de la prueba")
    prueba_code: str = Field(..., max_length=20, description="Código único de la prueba")
    prueba_description: Optional[str] = Field(None, max_length=500, description="Descripción de la prueba")
    tiempo: Optional[int] = Field(None, gt=0, max_value=1440, description="Tiempo estimado en minutos")
    is_active: bool = Field(default=True, description="Estado activo de la prueba")

    @validator('prueba_name')
    def validate_prueba_name(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de la prueba no puede estar vacío')
        return v.strip()

    @validator('prueba_code')
    def validate_prueba_code(cls, v):
        if not v or not v.strip():
            raise ValueError('El código de la prueba no puede estar vacío')
        return v.strip().upper()

    @validator('tiempo')
    def validate_tiempo(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El tiempo debe ser mayor a 0')
        if v is not None and v > 1440:
            raise ValueError('El tiempo no puede exceder 24 horas (1440 minutos)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prueba_name": "Hemoglobina",
                "prueba_code": "HB001",
                "prueba_description": "Análisis de hemoglobina en sangre",
                "tiempo": 30,
                "is_active": True
            }
        }


class PruebaUpdate(BaseModel):
    """Esquema para actualizar una prueba"""
    prueba_name: Optional[str] = Field(None, max_length=200, description="Nombre de la prueba")
    prueba_code: Optional[str] = Field(None, max_length=20, description="Código único de la prueba")
    prueba_description: Optional[str] = Field(None, max_length=500, description="Descripción de la prueba")
    tiempo: Optional[int] = Field(None, gt=0, max_value=1440, description="Tiempo estimado en minutos")
    is_active: Optional[bool] = Field(None, description="Estado activo de la prueba")

    @validator('prueba_name')
    def validate_prueba_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El nombre de la prueba no puede estar vacío')
            return v.strip()
        return v

    @validator('prueba_code')
    def validate_prueba_code(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El código de la prueba no puede estar vacío')
            return v.strip().upper()
        return v

    @validator('tiempo')
    def validate_tiempo(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El tiempo debe ser mayor a 0')
        if v is not None and v > 1440:
            raise ValueError('El tiempo no puede exceder 24 horas (1440 minutos)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prueba_name": "Hemoglobina Actualizada",
                "tiempo": 45,
                "prueba_description": "Análisis completo de hemoglobina"
            }
        }


class PruebaResponse(BaseModel):
    """Esquema de respuesta para prueba"""
    id: str = Field(..., description="ID único de la prueba")
    prueba_name: str = Field(..., description="Nombre de la prueba")
    prueba_code: str = Field(..., description="Código único de la prueba")
    prueba_description: Optional[str] = Field(None, description="Descripción de la prueba")
    tiempo: Optional[int] = Field(None, description="Tiempo estimado en minutos")
    is_active: bool = Field(..., description="Estado activo de la prueba")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de actualización")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "64f8a1b2c3d4e5f6a7b8c9d0",
                "prueba_name": "Hemoglobina",
                "prueba_code": "HB001",
                "prueba_description": "Análisis de hemoglobina en sangre",
                "tiempo": 30,
                "is_active": True,
                "fecha_creacion": "2023-09-07T10:30:00Z",
                "fecha_actualizacion": None
            }
        }


class PruebaSearch(BaseModel):
    """Esquema para búsqueda de pruebas"""
    query: Optional[str] = Field(None, description="Término de búsqueda")
    activo: Optional[bool] = Field(None, description="Filtrar por estado activo")
    skip: int = Field(default=0, ge=0, description="Número de registros a omitir")
    limit: int = Field(default=10, ge=1, le=1000, description="Número máximo de registros")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "hemoglobina",
                "activo": True,
                "skip": 0,
                "limit": 10
            }
        }


class PruebasListResponse(BaseModel):
    """Esquema de respuesta para lista de pruebas"""
    pruebas: list[PruebaResponse] = Field(..., description="Lista de pruebas")
    total: int = Field(..., description="Total de pruebas encontradas")
    skip: int = Field(..., description="Registros omitidos")
    limit: int = Field(..., description="Límite de registros")
    has_next: bool = Field(..., description="¿Hay más páginas?")
    has_prev: bool = Field(..., description="¿Hay páginas anteriores?")

    class Config:
        json_schema_extra = {
            "example": {
                "pruebas": [
                    {
                        "id": "64f8a1b2c3d4e5f6a7b8c9d0",
                        "prueba_name": "Hemoglobina",
                        "prueba_code": "HB001",
                        "prueba_description": "Análisis de hemoglobina en sangre",
                        "tiempo": 30,
                        "is_active": True,
                        "fecha_creacion": "2023-09-07T10:30:00Z",
                        "fecha_actualizacion": None
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10,
                "has_next": False,
                "has_prev": False
            }
        }


class PruebasItem(BaseModel):
    """Esquema para items de pruebas en casos"""
    id: str = Field(..., description="ID único de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    cantidad: int = Field(default=1, ge=1, le=10, description="Cantidad/multiplicador de la prueba")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "64f8a1b2c3d4e5f6a7b8c9d0",
                "nombre": "Hemoglobina",
                "cantidad": 1
            }
        }
