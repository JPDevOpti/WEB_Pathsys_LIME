"""Esquemas para el modelo Patólogo"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class PatologoCreate(BaseModel):
    """Esquema para crear un nuevo patólogo"""
    patologoName: str = Field(..., min_length=2, max_length=100, description="Nombre completo del patólogo")
    InicialesPatologo: str = Field(..., min_length=2, max_length=10, description="Iniciales del patólogo")
    patologoCode: str = Field(..., min_length=6, max_length=11, description="Código único de 6-11 caracteres")
    PatologoEmail: EmailStr = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., min_length=5, max_length=50, description="Número de registro médico único")
    password: str = Field(..., min_length=6, max_length=100, description="Contraseña para el usuario del patólogo")
    isActive: bool = Field(default=True, description="Estado activo/inactivo del patólogo")
    firma: str = Field(default="", description="URL de firma digital, por defecto vacío")
    observaciones: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    class Config:
        populate_by_name = True

class PatologoUpdate(BaseModel):
    """Esquema para actualizar un patólogo existente"""
    patologoName: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre completo del patólogo")
    InicialesPatologo: Optional[str] = Field(None, min_length=2, max_length=10, description="Iniciales del patólogo")
    patologoCode: Optional[str] = Field(None, min_length=6, max_length=11, description="Código único de 6-11 caracteres")
    PatologoEmail: Optional[EmailStr] = Field(None, description="Email único del patólogo")
    registro_medico: Optional[str] = Field(None, min_length=5, max_length=50, description="Número de registro médico único")
    isActive: Optional[bool] = Field(None, description="Estado activo/inactivo del patólogo")
    # firma removida de actualización por requerimiento
    observaciones: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    # Cambio opcional de contraseña del usuario vinculado (no se persiste en colección patólogos)
    password: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=100,
        description="Nueva contraseña para el usuario del patólogo",
        exclude=True
    )
    
    class Config:
        populate_by_name = True

class PatologoResponse(BaseModel):
    """Esquema para respuesta de patólogo"""
    id: str = Field(..., description="ID único del patólogo")
    patologoName: str = Field(..., description="Nombre completo del patólogo")
    InicialesPatologo: Optional[str] = Field(None, description="Iniciales del patólogo")
    patologoCode: str = Field(..., description="Código único de 6-11 caracteres")
    PatologoEmail: EmailStr = Field(..., description="Email único del patólogo")
    registro_medico: str = Field(..., description="Número de registro médico único")
    isActive: bool = Field(..., description="Estado activo/inactivo del patólogo")
    firma: str = Field(..., description="URL de firma digital")
    observaciones: Optional[str] = Field(None, description="Notas adicionales")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")
    fecha_actualizacion: datetime = Field(..., description="Fecha de última actualización")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class PatologoEstadoUpdate(BaseModel):
    """Esquema para cambiar el estado de un patólogo"""
    isActive: bool = Field(..., description="Nuevo estado activo/inactivo del patólogo")
    
    class Config:
        populate_by_name = True

class PatologoSearch(BaseModel):
    """Esquema para búsqueda avanzada de patólogos"""
    q: Optional[str] = Field(None, description="Búsqueda general")
    patologoName: Optional[str] = Field(None, description="Filtrar por nombre")
    patologoCode: Optional[str] = Field(None, description="Filtrar por código")
    PatologoEmail: Optional[str] = Field(None, description="Filtrar por email")
    registro_medico: Optional[str] = Field(None, description="Filtrar por registro médico")
    isActive: Optional[bool] = Field(None, description="Filtrar por estado activo")
    observaciones: Optional[str] = Field(None, description="Filtrar por observaciones")
    
    class Config:
        populate_by_name = True

class PatologoFirmaUpdate(BaseModel):
    """Esquema para actualizar la firma de un patólogo"""
    firma: str = Field(..., description="URL de la firma digital del patólogo")
    
    class Config:
        populate_by_name = True