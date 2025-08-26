"""Esquemas para tokens"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Token(BaseModel):
    """Esquema para token de acceso"""
    access_token: str = Field(..., description="Token de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenPayload(BaseModel):
    """Esquema para payload del token"""
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="Email del usuario")
    username: str = Field(..., description="Nombre de usuario")
    roles: List[str] = Field(..., description="Roles del usuario")
    exp: datetime = Field(..., description="Fecha de expiración")
    iat: datetime = Field(..., description="Fecha de emisión")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sub": "507f1f77bcf86cd799439011",
                "email": "usuario@ejemplo.com",
                "username": "usuario",
                "roles": ["patologo"],
                "exp": "2024-01-01T12:00:00Z",
                "iat": "2024-01-01T11:00:00Z"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Esquema para solicitud de refresh token"""
    refresh_token: str = Field(..., description="Token de actualización")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }