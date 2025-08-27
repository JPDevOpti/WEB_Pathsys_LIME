from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.shared.models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel

class AuxiliarEmail(BaseModel):
    """Esquema para validación de email de auxiliar"""
    auxiliar_email: EmailStr = Field(..., description="Email del auxiliar")

class AuxiliarCreate(BaseCreateModel, AuxiliarEmail):
    """Esquema para crear un auxiliar"""
    auxiliar_name: str = Field(..., min_length=2, max_length=200, description="Nombre del auxiliar")
    auxiliar_code: str = Field(..., min_length=8, max_length=20, description="Código único del auxiliar")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña para el usuario del auxiliar")
    is_active: bool = Field(default=True, description="Estado activo del auxiliar")
    observaciones: Optional[str] = Field(default="", max_length=500, description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "auxiliar_name": "Ana María González",
                "auxiliar_code": "AUX001",
                "auxiliar_email": "ana.gonzalez@laboratorio.com",
                "password": "auxiliar123",
                "is_active": True,
                "observaciones": "Auxiliar de laboratorio con experiencia"
            }
        }

class AuxiliarUpdate(BaseUpdateModel):
    """Esquema para actualizar un auxiliar"""
    auxiliar_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Nombre del auxiliar")
    auxiliar_code: Optional[str] = Field(None, min_length=8, max_length=20, description="Código único del auxiliar")
    auxiliar_email: Optional[EmailStr] = Field(None, description="Email del auxiliar")
    is_active: Optional[bool] = Field(None, description="Estado activo del auxiliar")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    # Campo opcional para cambio de contraseña del usuario vinculado (excluido de persistencia en auxiliares)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128, description="Nueva contraseña para el usuario del auxiliar", exclude=True)
    
    class Config:
        populate_by_name = True

class AuxiliarResponse(BaseResponseModel):
    """Esquema de respuesta para auxiliar"""
    auxiliar_name: str = Field(..., description="Nombre del auxiliar")
    auxiliar_code: str = Field(..., description="Código único del auxiliar")
    auxiliar_email: EmailStr = Field(..., description="Email del auxiliar")
    is_active: bool = Field(..., description="Estado activo del auxiliar")
    observaciones: str = Field(..., description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "auxiliar_name": "Ana María González",
                "auxiliar_code": "AUX001",
                "auxiliar_email": "ana.gonzalez@laboratorio.com",
                "is_active": True,
                "observaciones": "Auxiliar de laboratorio con experiencia",
                "fecha_creacion": "2024-01-15T10:30:00",
                "fecha_actualizacion": "2024-01-15T10:30:00"
            }
        }

class AuxiliarSearch(BaseModel):
    """Esquema para búsqueda de auxiliares"""
    auxiliar_name: Optional[str] = Field(None, description="Nombre del auxiliar para búsqueda")
    auxiliar_code: Optional[str] = Field(None, description="Código del auxiliar para búsqueda")
    auxiliar_email: Optional[str] = Field(None, description="Email del auxiliar para búsqueda")
    is_active: Optional[bool] = Field(None, description="Estado activo para filtrar")
    
    class Config:
        populate_by_name = True

class AuxiliarEstadoUpdate(BaseModel):
    """Esquema para actualizar solo el estado del auxiliar"""
    is_active: bool = Field(..., description="Nuevo estado activo del auxiliar")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "is_active": False
            }
        }