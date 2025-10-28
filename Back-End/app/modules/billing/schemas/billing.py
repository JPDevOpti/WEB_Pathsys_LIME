"""Esquemas para el modelo Billing"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

class BillingBase(BaseModel):
    """Esquema base para Billing"""
    billing_code: str = Field(..., max_length=11, description="Código único del usuario de facturación")
    billing_name: str = Field(..., max_length=100, description="Nombre completo del usuario de facturación")
    billing_email: EmailStr = Field(..., description="Email único del usuario de facturación")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del usuario de facturación")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    model_config = ConfigDict(populate_by_name=True)

class BillingCreate(BillingBase):
    """Esquema para crear un nuevo usuario de facturación"""
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del usuario de facturación")

class BillingUpdate(BaseModel):
    """Esquema para actualizar un usuario de facturación existente"""
    billing_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del usuario de facturación")
    billing_email: Optional[EmailStr] = Field(None, description="Email único del usuario de facturación")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo del usuario de facturación")
    observations: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    password: Optional[str] = Field(None, min_length=6, max_length=128, description="Nueva contraseña del usuario de facturación")

    model_config = ConfigDict(populate_by_name=True)

class BillingResponse(BillingBase):
    """Esquema para respuesta de usuario de facturación"""
    id: str = Field(..., description="ID único del usuario de facturación")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BillingSearch(BaseModel):
    """Esquema para búsqueda de usuarios de facturación"""
    q: Optional[str] = Field(None, description="Término de búsqueda general")
    billing_name: Optional[str] = Field(None, description="Filtrar por nombre")
    billing_code: Optional[str] = Field(None, description="Filtrar por código")
    billing_email: Optional[str] = Field(None, description="Filtrar por email")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")

    model_config = ConfigDict(populate_by_name=True)
