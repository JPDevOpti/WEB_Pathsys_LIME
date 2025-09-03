"""Esquemas para el modelo Patólogo"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class PatologoCreate(BaseModel):
    """Esquema para crear un nuevo patólogo"""
    patologo_name: str = Field(..., max_length=100, description="Nombre completo del patólogo")
    iniciales_patologo: str = Field(..., max_length=10, description="Iniciales del patólogo")
    patologo_code: str = Field(..., max_length=10, description="Código único del patólogo")
    patologo_email: EmailStr = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., max_length=50, description="Número de registro médico único")
    password: str = Field(..., max_length=100, description="Contraseña para el usuario del patólogo")
    is_active: bool = Field(default=True, description="Estado activo/inactivo del patólogo")
    firma: str = Field(default="", description="URL de firma digital, por defecto vacío")
    observaciones: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    class Config:
        populate_by_name = True

class PatologoUpdate(BaseModel):
    """Esquema para actualizar un patólogo existente"""
    patologo_name: Optional[str] = Field(None, max_length=100, description="Nombre completo del patólogo")
    iniciales_patologo: Optional[str] = Field(None, max_length=10, description="Iniciales del patólogo")
    patologo_code: Optional[str] = Field(None, max_length=10, description="Código único del patólogo")
    patologo_email: Optional[EmailStr] = Field(None, description="Email único del patólogo")
    registro_medico: Optional[str] = Field(None, max_length=50, description="Número de registro médico único")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo del patólogo")
    # firma removida de actualización por requerimiento
    observaciones: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    # Cambio opcional de contraseña del usuario vinculado (no se persiste en colección patólogos)
    password: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nueva contraseña para el usuario del patólogo",
        exclude=True
    )
    
    class Config:
        populate_by_name = True

class PatologoResponse(BaseModel):
    """Esquema para respuesta de patólogo"""
    id: str = Field(..., description="ID único del patólogo")
    patologo_name: str = Field(..., description="Nombre completo del patólogo")
    iniciales_patologo: Optional[str] = Field(None, description="Iniciales del patólogo")
    patologo_code: str = Field(..., description="Código único de 6-10 caracteres")
    patologo_email: EmailStr = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., description="Número de registro médico único")
    is_active: bool = Field(..., description="Estado activo/inactivo del patólogo")
    firma: str = Field(..., description="URL de firma digital")
    observaciones: Optional[str] = Field(None, description="Notas adicionales")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class PatologoEstadoUpdate(BaseModel):
    """Esquema para cambiar el estado de un patólogo"""
    is_active: bool = Field(..., description="Nuevo estado activo/inactivo del patólogo")
    
    class Config:
        populate_by_name = True

class PatologoSearch(BaseModel):
    """Esquema para búsqueda avanzada de patólogos"""
    q: Optional[str] = Field(None, description="Búsqueda general")
    patologo_name: Optional[str] = Field(None, description="Filtrar por nombre")
    patologo_code: Optional[str] = Field(None, description="Filtrar por código")
    patologo_email: Optional[str] = Field(None, description="Filtrar por email")
    registro_medico: Optional[str] = Field(None, description="Filtrar por registro médico")
    is_active: Optional[bool] = Field(None, description="Filtrar por estado activo")
    observaciones: Optional[str] = Field(None, description="Filtrar por observaciones")
    
    class Config:
        populate_by_name = True

class PatologoFirmaUpdate(BaseModel):
    """Esquema para actualizar la firma de un patólogo"""
    firma: str = Field(..., description="URL de la firma digital del patólogo")
    
    class Config:
        populate_by_name = True