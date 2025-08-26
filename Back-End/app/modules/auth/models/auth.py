"""Modelos de autenticación"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.shared.schemas.common import RolEnum


class AuthUser(BaseModel):
    """Modelo de usuario para autenticación"""
    id: str = Field(..., description="ID del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: Optional[str] = Field(None, description="Nombre completo del usuario")
    # Compatibilidad con diferentes campos de nombre
    nombres: Optional[str] = Field(None, description="Nombres del usuario")
    apellidos: Optional[str] = Field(None, description="Apellidos del usuario")
    username: Optional[str] = Field(None, description="Nombre de usuario")
    # Manejar tanto 'rol' como 'roles' para compatibilidad
    rol: Optional[Union[RolEnum, str]] = Field(None, description="Rol principal del usuario")
    roles: Optional[List[Union[RolEnum, str]]] = Field(None, description="Roles del usuario")
    # Manejar tanto 'activo' como 'is_active'
    activo: Optional[bool] = Field(None, description="Estado del usuario")
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de actualización")
    ultimo_acceso: Optional[datetime] = Field(None, description="Último acceso")
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Datos del token de autenticación"""
    user_id: str = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    rol: str = Field(..., description="Rol del usuario")
    exp: datetime = Field(..., description="Fecha de expiración")
    iat: datetime = Field(..., description="Fecha de emisión")
    
    class Config:
        from_attributes = True