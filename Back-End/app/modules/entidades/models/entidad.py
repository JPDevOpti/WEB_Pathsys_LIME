from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class EntidadBase(BaseModel):
    """Modelo base para entidades"""
    entidad_name: str = Field(..., min_length=2, max_length=200, description="Nombre de la entidad")
    entidad_code: str = Field(..., min_length=2, max_length=20, description="Código único de la entidad")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones o comentarios")
    is_active: bool = Field(True, description="Estado activo de la entidad")

    @validator('entidad_name')
    def validate_entidad_name(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de la entidad no puede estar vacío')
        return v.strip()

    @validator('entidad_code')
    def validate_entidad_code(cls, v):
        if not v or not v.strip():
            raise ValueError('El código de la entidad no puede estar vacío')
        return v.strip().upper()


class EntidadCreate(EntidadBase):
    """Modelo para crear una entidad"""
    pass


class EntidadUpdate(BaseModel):
    """Modelo para actualizar una entidad"""
    entidad_name: Optional[str] = Field(None, min_length=2, max_length=200)
    entidad_code: Optional[str] = Field(None, min_length=2, max_length=20)
    observaciones: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @validator('entidad_name')
    def validate_entidad_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El nombre de la entidad no puede estar vacío')
            return v.strip()
        return v

    @validator('entidad_code')
    def validate_entidad_code(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El código de la entidad no puede estar vacío')
            return v.strip().upper()
        return v


class EntidadResponse(EntidadBase):
    """Modelo de respuesta para entidades"""
    id: Optional[str] = Field(None, alias="_id")
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }
        validate_by_name = True


class EntidadSearch(BaseModel):
    """Modelo para búsqueda de entidades"""
    query: Optional[str] = None
    activo: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class Entidad(EntidadBase):
    """Modelo completo de entidad"""
    id: Optional[str] = Field(None, alias="_id")
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }
        validate_by_name = True