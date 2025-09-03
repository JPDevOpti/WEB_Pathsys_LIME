"""Esquemas para login"""

from typing import List
from pydantic import BaseModel, Field, EmailStr
from app.shared.schemas.common import RolEnum


class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., max_length=128, description="Contraseña del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "mi_contraseña_segura"
            }
        }


class LoginResponse(BaseModel):
    """Esquema para respuesta de login"""
    access_token: str = Field(..., description="Token de acceso")
    refresh_token: str = Field(..., description="Token de actualización")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: dict = Field(..., description="Información del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "email": "usuario@ejemplo.com",
                    "nombre": "Juan Pérez",
                    "rol": "patologo",
                    "roles": ["patologo"]
                }
            }
        }