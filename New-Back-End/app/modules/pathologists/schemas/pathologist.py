"""Esquemas para el modelo Pathologist"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class PathologistBase(BaseModel):
    """Esquema base para Pathologist"""
    pathologist_code: str = Field(..., max_length=11, description="Código único del patólogo")
    pathologist_name: str = Field(..., max_length=100, description="Nombre completo del patólogo")
    initials: Optional[str] = Field(None, max_length=10, description="Iniciales del patólogo")
    pathologist_email: EmailStr = Field(..., description="Email único del patólogo")
    medical_license: str = Field(..., max_length=50, description="Número de licencia médica única")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del patólogo")
    signature: str = Field(default="", description="URL de firma digital")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    class Config:
        populate_by_name = True

class PathologistCreate(PathologistBase):
    """Esquema para crear un nuevo patólogo"""
    pass

class PathologistUpdate(BaseModel):
    """Esquema para actualizar un patólogo existente"""
    pathologist_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del patólogo")
    initials: Optional[str] = Field(None, max_length=10, description="Iniciales del patólogo")
    pathologist_email: Optional[EmailStr] = Field(None, description="Email único del patólogo")
    medical_license: Optional[str] = Field(None, max_length=50, description="Número de licencia médica única")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo del patólogo")
    signature: Optional[str] = Field(None, description="URL de firma digital")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    class Config:
        populate_by_name = True

class PathologistResponse(PathologistBase):
    """Esquema para respuesta de patólogo"""
    id: str = Field(..., description="ID único del patólogo")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True
        populate_by_name = True

class PathologistSearch(BaseModel):
    """Esquema para búsqueda de patólogos"""
    q: Optional[str] = Field(None, description="Término de búsqueda general")
    pathologist_name: Optional[str] = Field(None, description="Filtrar por nombre")
    pathologist_code: Optional[str] = Field(None, description="Filtrar por código")
    pathologist_email: Optional[str] = Field(None, description="Filtrar por email")
    medical_license: Optional[str] = Field(None, description="Filtrar por licencia médica")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")

    class Config:
        populate_by_name = True
