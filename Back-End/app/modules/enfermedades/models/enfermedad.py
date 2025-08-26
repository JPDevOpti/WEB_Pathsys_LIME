from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class EnfermedadBase(BaseModel):
    """Modelo base para enfermedad"""
    tabla: str = Field(..., description="Tabla de referencia (ej: CIE10)")
    codigo: str = Field(..., description="Código de la enfermedad")
    nombre: str = Field(..., description="Nombre de la enfermedad")
    descripcion: Optional[str] = Field(None, description="Descripción general de la enfermedad")
    isActive: bool = Field(True, description="Estado activo de la enfermedad")


class EnfermedadCreate(EnfermedadBase):
    """Modelo para crear una enfermedad"""
    pass


class EnfermedadUpdate(BaseModel):
    """Modelo para actualizar una enfermedad"""
    tabla: Optional[str] = Field(None, description="Tabla de referencia")
    codigo: Optional[str] = Field(None, description="Código de la enfermedad")
    nombre: Optional[str] = Field(None, description="Nombre de la enfermedad")
    descripcion: Optional[str] = Field(None, description="Descripción general de la enfermedad")
    isActive: Optional[bool] = Field(None, description="Estado activo de la enfermedad")


class EnfermedadInDB(EnfermedadBase):
    """Modelo para enfermedad en la base de datos"""
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        from_attributes = True


class EnfermedadResponse(EnfermedadBase):
    """Modelo para respuesta de enfermedad"""
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        from_attributes = True
