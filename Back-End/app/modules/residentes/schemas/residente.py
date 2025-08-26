from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.shared.models.base import BaseCreateModel, BaseUpdateModel, BaseResponseModel

class ResidenteEmail(BaseModel):
    """Esquema para validación de email de residente"""
    ResidenteEmail: EmailStr = Field(..., description="Email del residente")

class ResidenteCreate(BaseCreateModel, ResidenteEmail):
    """Esquema para crear un residente"""
    residenteName: str = Field(..., min_length=2, max_length=100, description="Nombre del residente")
    InicialesResidente: str = Field(..., min_length=2, max_length=10, description="Iniciales del residente")
    residenteCode: str = Field(..., min_length=3, max_length=20, description="Código único del residente")
    registro_medico: str = Field(..., min_length=3, max_length=50, description="Número de registro médico")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña para el usuario del residente")
    isActive: bool = Field(default=True, description="Estado activo del residente")
    observaciones: Optional[str] = Field(default="", max_length=500, description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "residenteName": "Dr. Juan Pérez",
                "InicialesResidente": "JP",
                "residenteCode": "RES001",
                "ResidenteEmail": "juan.perez@hospital.com",
                "registro_medico": "12345",
                "password": "residente123",
                "isActive": True,
                "observaciones": "Residente de primer año"
            }
        }

class ResidenteUpdate(BaseUpdateModel):
    """Esquema para actualizar un residente"""
    residenteName: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre del residente")
    InicialesResidente: Optional[str] = Field(None, min_length=2, max_length=10, description="Iniciales del residente")
    residenteCode: Optional[str] = Field(None, min_length=3, max_length=20, description="Código único del residente")
    ResidenteEmail: Optional[EmailStr] = Field(None, description="Email del residente")
    registro_medico: Optional[str] = Field(None, min_length=3, max_length=50, description="Número de registro médico")
    isActive: Optional[bool] = Field(None, description="Estado activo del residente")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    # Campo opcional para cambio de contraseña del usuario vinculado (excluido de persistencia en residentes)
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=100,
        description="Nueva contraseña para el usuario del residente",
        exclude=True
    )
    
    class Config:
        populate_by_name = True

class ResidenteResponse(BaseResponseModel):
    """Esquema de respuesta para residente"""
    residenteName: str = Field(..., description="Nombre del residente")
    InicialesResidente: str = Field(default="", description="Iniciales del residente")
    residenteCode: str = Field(..., description="Código único del residente")
    ResidenteEmail: str = Field(..., description="Email del residente")
    registro_medico: str = Field(..., description="Número de registro médico")
    isActive: bool = Field(..., description="Estado activo del residente")
    observaciones: str = Field(default="", description="Observaciones adicionales")
    
    class Config:
        populate_by_name = True

class ResidenteSearch(BaseModel):
    """Esquema para búsqueda avanzada de residentes"""
    residenteName: Optional[str] = Field(None, description="Nombre del residente")
    InicialesResidente: Optional[str] = Field(None, description="Iniciales del residente")
    residenteCode: Optional[str] = Field(None, description="Código del residente")
    ResidenteEmail: Optional[str] = Field(None, description="Email del residente")
    registro_medico: Optional[str] = Field(None, description="Número de registro médico")
    isActive: Optional[bool] = Field(None, description="Estado activo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "residenteName": "Juan",
                "InicialesResidente": "JP",
                "residenteCode": "RES",
                "ResidenteEmail": "juan@hospital.com",
                "registro_medico": "123",
                "isActive": True
            }
        }

class ResidenteEstadoUpdate(BaseModel):
    """Esquema para actualizar el estado de un residente"""
    isActive: bool = Field(..., description="Estado activo del residente")
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "isActive": False
            }
        }