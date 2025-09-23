from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.shared.models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel

class ResidenteEmail(BaseModel):
    """Esquema para validación de email de residente"""
    residente_email: EmailStr = Field(..., description="Email del residente")

class ResidenteCreate(BaseCreateModel, ResidenteEmail):
    """Esquema para crear un residente"""
    residente_name: str = Field(..., max_length=100, description="Nombre del residente")
    iniciales_residente: str = Field(..., max_length=10, description="Iniciales del residente")
    residente_code: str = Field(..., max_length=20, description="Código único del residente")
    registro_medico: str = Field(..., max_length=50, description="Número de registro médico")
    password: str = Field(..., max_length=100, description="Contraseña para el usuario del residente")
    is_active: bool = Field(default=True, description="Estado activo del residente")
    observaciones: Optional[str] = Field(default="", max_length=500, description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "residente_name": "Dr. Juan Pérez",
                "iniciales_residente": "JP",
                "residente_code": "12345678",
                "residente_email": "juan.perez@hospital.com",
                "registro_medico": "12345",
                "password": "residente123",
                "is_active": True,
                "observaciones": "Residente de primer año"
            }
        }

class ResidenteUpdate(BaseUpdateModel):
    """Esquema para actualizar un residente"""
    residente_name: Optional[str] = Field(None, max_length=100, description="Nombre del residente")
    iniciales_residente: Optional[str] = Field(None, max_length=10, description="Iniciales del residente")
    residente_code: Optional[str] = Field(None, max_length=20, description="Código único del residente")
    residente_email: Optional[EmailStr] = Field(None, description="Email del residente")
    registro_medico: Optional[str] = Field(None, max_length=50, description="Número de registro médico")
    is_active: Optional[bool] = Field(None, description="Estado activo del residente")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    # Campo opcional para cambio de contraseña del usuario vinculado (excluido de persistencia en residentes)
    password: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nueva contraseña para el usuario del residente",
        exclude=True
    )
    
    class Config:
        populate_by_name = True

class ResidenteResponse(BaseResponseModel):
    """Esquema de respuesta para residente"""
    residente_name: str = Field(..., description="Nombre del residente")
    iniciales_residente: str = Field(default="", description="Iniciales del residente")
    residente_code: str = Field(..., description="Código único del residente")
    residente_email: str = Field(..., description="Email del residente")
    registro_medico: str = Field(..., description="Número de registro médico")
    is_active: bool = Field(..., description="Estado activo del residente")
    observaciones: str = Field(default="", description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True

class ResidenteSearch(BaseModel):
    """Esquema para búsqueda avanzada de residentes"""
    q: Optional[str] = Field(None, description="Búsqueda general")
    residente_name: Optional[str] = Field(None, description="Nombre del residente")
    iniciales_residente: Optional[str] = Field(None, description="Iniciales del residente")
    residente_code: Optional[str] = Field(None, description="Código del residente")
    residente_email: Optional[str] = Field(None, description="Email del residente")
    registro_medico: Optional[str] = Field(None, description="Número de registro médico")
    is_active: Optional[bool] = Field(None, description="Estado activo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "q": "Juan",
                "residente_name": "Juan",
                "iniciales_residente": "JP",
                "residente_code": "12345678",
                "residente_email": "juan@hospital.com",
                "registro_medico": "123",
                "is_active": True
            }
        }

class ResidenteEstadoUpdate(BaseModel):
    """Esquema para actualizar el estado de un residente"""
    is_active: bool = Field(..., description="Estado activo del residente")
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "is_active": False
            }
        }