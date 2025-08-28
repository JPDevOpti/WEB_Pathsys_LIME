"""Esquemas para administradores"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime


class AdministratorCreate(BaseModel):
    """Esquema para crear un nuevo administrador"""
    nombre: str = Field(..., min_length=2, max_length=200, description="Nombre completo del administrador")
    email: EmailStr = Field(..., description="Email único del administrador")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del administrador")
    is_active: bool = Field(default=True, description="Estado activo del administrador")
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre del administrador no puede estar vacío')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        if len(v) > 128:
            raise ValueError('La contraseña no puede tener más de 128 caracteres')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pablo Restrepo",
                "email": "juan.restrepo183@udea.edu.co",
                "password": "Nomerobe-12345",
                "is_active": True
            }
        }


class AdministratorUpdate(BaseModel):
    """Esquema para actualizar un administrador existente"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=200, description="Nombre completo del administrador")
    email: Optional[EmailStr] = Field(None, description="Email único del administrador")
    is_active: Optional[bool] = Field(None, description="Estado activo del administrador")
    password: Optional[str] = Field(
        None, 
        min_length=6, 
        max_length=128, 
        description="Nueva contraseña (opcional)",
        exclude=True
    )
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El nombre del administrador no puede estar vacío')
            return v.strip()
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 6:
                raise ValueError('La contraseña debe tener al menos 6 caracteres')
            if len(v) > 128:
                raise ValueError('La contraseña no puede tener más de 128 caracteres')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pablo Restrepo Actualizado",
                "email": "juan.restrepo183@udea.edu.co",
                "is_active": True
            }
        }


class AdministratorResponse(BaseModel):
    """Esquema para respuesta de administrador"""
    id: str = Field(..., description="ID único del administrador")
    nombre: str = Field(..., description="Nombre completo del administrador")
    email: EmailStr = Field(..., description="Email único del administrador")
    rol: str = Field(default="administrador", description="Rol del administrador")
    is_active: bool = Field(..., description="Estado activo del administrador")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "64f8a1b2c3d4e5f6a7b8c9d0",
                "nombre": "Juan Pablo Restrepo",
                "email": "juan.restrepo183@udea.edu.co",
                "rol": "administrador",
                "is_active": True,
                "fecha_creacion": "2023-09-07T10:30:00Z",
                "fecha_actualizacion": "2023-09-07T10:30:00Z"
            }
        }


class AdministratorSearch(BaseModel):
    """Esquema para búsqueda de administradores"""
    q: Optional[str] = Field(None, description="Búsqueda general por nombre o email")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")
    skip: int = Field(0, ge=0, description="Número de registros a omitir")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de registros")
    
    class Config:
        json_schema_extra = {
            "example": {
                "q": "Juan",
                "is_active": True,
                "skip": 0,
                "limit": 10
            }
        }
