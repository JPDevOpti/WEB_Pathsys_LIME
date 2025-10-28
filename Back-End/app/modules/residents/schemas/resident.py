"""Esquemas para el modelo Resident"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

class ResidentBase(BaseModel):
    """Esquema base para Resident"""
    resident_code: str = Field(..., max_length=11, description="Código único del residente")
    resident_name: str = Field(..., max_length=100, description="Nombre completo del residente")
    initials: Optional[str] = Field(None, max_length=10, description="Iniciales del residente")
    resident_email: EmailStr = Field(..., description="Email único del residente")
    medical_license: str = Field(..., max_length=50, description="Número de licencia médica única")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del residente")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    model_config = ConfigDict(populate_by_name=True)

class ResidentCreate(ResidentBase):
    """Esquema para crear un nuevo residente"""
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del residente")

class ResidentUpdate(BaseModel):
    """Esquema para actualizar un residente existente"""
    resident_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del residente")
    initials: Optional[str] = Field(None, max_length=10, description="Iniciales del residente")
    resident_email: Optional[EmailStr] = Field(None, description="Email único del residente")
    medical_license: Optional[str] = Field(None, max_length=50, description="Número de licencia médica única")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo del residente")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="Nueva contraseña del residente")

    model_config = ConfigDict(populate_by_name=True)

class ResidentResponse(ResidentBase):
    """Esquema para respuesta de residente"""
    id: str = Field(..., description="ID único del residente")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ResidentSearch(BaseModel):
    """Esquema para búsqueda de residentes"""
    q: Optional[str] = Field(None, description="Término de búsqueda general")
    resident_name: Optional[str] = Field(None, description="Filtrar por nombre")
    resident_code: Optional[str] = Field(None, description="Filtrar por código")
    resident_email: Optional[str] = Field(None, description="Filtrar por email")
    medical_license: Optional[str] = Field(None, description="Filtrar por licencia médica")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")

    model_config = ConfigDict(populate_by_name=True)
