from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.shared.models.base import PyObjectId


class PruebaBase(BaseModel):
    """Modelo base para Prueba"""
    pruebasName: str = Field(..., description="Nombre de la prueba")
    pruebaCode: str = Field(..., description="Código único de la prueba")
    pruebasDescription: Optional[str] = Field(None, description="Descripción de la prueba")
    tiempo: Optional[int] = Field(None, description="Tiempo estimado en horas")
    isActive: bool = Field(default=True, description="Estado activo de la prueba")


class PruebaCreate(PruebaBase):
    """Modelo para crear una nueva prueba"""
    pass


class PruebaUpdate(BaseModel):
    """Modelo para actualizar una prueba"""
    pruebasName: Optional[str] = None
    pruebaCode: Optional[str] = None
    pruebasDescription: Optional[str] = None
    tiempo: Optional[int] = None
    isActive: Optional[bool] = None


class PruebaResponse(PruebaBase):
    """Modelo de respuesta para prueba"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Prueba(PruebaBase):
    """Modelo completo de prueba para la base de datos"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PruebaSearch(BaseModel):
    """Modelo para búsqueda de pruebas"""
    query: Optional[str] = None
    activo: Optional[bool] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=1000)


class PruebasItem(BaseModel):
    """Modelo para items de pruebas en casos"""
    id: str = Field(..., description="ID único de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")