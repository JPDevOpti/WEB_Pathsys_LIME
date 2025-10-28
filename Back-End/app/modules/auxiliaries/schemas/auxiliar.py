"""Esquemas para el modelo Auxiliar"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

class AuxiliarBase(BaseModel):
    """Esquema base para Auxiliar"""
    auxiliar_code: str = Field(..., max_length=11, description="Código único del auxiliar")
    auxiliar_name: str = Field(..., max_length=100, description="Nombre completo del auxiliar")
    auxiliar_email: EmailStr = Field(..., description="Email único del auxiliar")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del auxiliar")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    model_config = ConfigDict(populate_by_name=True)

class AuxiliarCreate(AuxiliarBase):
    """Esquema para crear un nuevo auxiliar"""
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del auxiliar")

class AuxiliarUpdate(BaseModel):
    """Esquema para actualizar un auxiliar existente"""
    auxiliar_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del auxiliar")
    auxiliar_email: Optional[EmailStr] = Field(None, description="Email único del auxiliar")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo del auxiliar")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="Nueva contraseña del auxiliar")

    model_config = ConfigDict(populate_by_name=True)

class AuxiliarResponse(AuxiliarBase):
    """Esquema para respuesta de auxiliar"""
    id: str = Field(..., description="ID único del auxiliar")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AuxiliarSearch(BaseModel):
    """Esquema para búsqueda de auxiliares"""
    q: Optional[str] = Field(None, description="Término de búsqueda general")
    auxiliar_name: Optional[str] = Field(None, description="Filtrar por nombre")
    auxiliar_code: Optional[str] = Field(None, description="Filtrar por código")
    auxiliar_email: Optional[str] = Field(None, description="Filtrar por email")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")

    model_config = ConfigDict(populate_by_name=True)
