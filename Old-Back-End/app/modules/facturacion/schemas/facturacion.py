from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.shared.models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel

class FacturacionEmail(BaseModel):
    """Esquema para validación de email de facturación"""
    facturacion_email: EmailStr = Field(..., description="Email del usuario de facturación")

class FacturacionCreate(BaseCreateModel, FacturacionEmail):
    """Esquema para crear un usuario de facturación"""
    facturacion_name: str = Field(..., max_length=200, description="Nombre del usuario de facturación")
    facturacion_code: str = Field(..., max_length=20, description="Código único del usuario de facturación")
    password: str = Field(..., max_length=128, description="Contraseña para el usuario de facturación")
    is_active: bool = Field(default=True, description="Estado activo del usuario de facturación")
    observaciones: Optional[str] = Field(default="", max_length=500, description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "facturacion_name": "Ana María González",
                "facturacion_code": "FAC001",
                "facturacion_email": "ana.gonzalez@facturacion.com",
                "password": "facturacion123",
                "is_active": True,
                "observaciones": "Usuario de facturación con experiencia"
            }
        }

class FacturacionUpdate(BaseUpdateModel):
    """Esquema para actualizar un usuario de facturación"""
    facturacion_name: Optional[str] = Field(None, max_length=200, description="Nombre del usuario de facturación")
    facturacion_code: Optional[str] = Field(None, max_length=20, description="Código único del usuario de facturación")
    facturacion_email: Optional[EmailStr] = Field(None, description="Email del usuario de facturación")
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario de facturación")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    password: Optional[str] = Field(default=None, max_length=128, description="Nueva contraseña para el usuario de facturación", exclude=True)
    
    class Config:
        populate_by_name = True

class FacturacionResponse(BaseResponseModel):
    """Esquema de respuesta para usuario de facturación"""
    facturacion_name: str = Field(..., description="Nombre del usuario de facturación")
    facturacion_code: str = Field(..., description="Código único del usuario de facturación")
    facturacion_email: EmailStr = Field(..., description="Email del usuario de facturación")
    is_active: bool = Field(..., description="Estado activo del usuario de facturación")
    observaciones: str = Field(..., description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "facturacion_name": "Ana María González",
                "facturacion_code": "FAC001",
                "facturacion_email": "ana.gonzalez@facturacion.com",
                "is_active": True,
                "observaciones": "Usuario de facturación con experiencia",
                "fecha_creacion": "2024-01-15T10:30:00",
                "fecha_actualizacion": "2024-01-15T10:30:00"
            }
        }

class FacturacionSearch(BaseModel):
    """Esquema para búsqueda de usuarios de facturación"""
    facturacion_name: Optional[str] = Field(None, description="Nombre del usuario de facturación para búsqueda")
    facturacion_code: Optional[str] = Field(None, description="Código del usuario de facturación para búsqueda")
    facturacion_email: Optional[str] = Field(None, description="Email del usuario de facturación para búsqueda")
    is_active: Optional[bool] = Field(None, description="Estado activo para filtrar")
    
    class Config:
        populate_by_name = True

class FacturacionEstadoUpdate(BaseModel):
    """Esquema para actualizar solo el estado del usuario de facturación"""
    is_active: bool = Field(..., description="Nuevo estado activo del usuario de facturación")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "is_active": False
            }
        }
