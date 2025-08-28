from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.modules.enfermedades.models.enfermedad import EnfermedadResponse


class EnfermedadCreateSchema(BaseModel):
    """Schema para crear una enfermedad"""
    tabla: str = Field(..., description="Tabla de referencia (ej: CIE10)")
    codigo: str = Field(..., description="Código de la enfermedad")
    nombre: str = Field(..., description="Nombre de la enfermedad")
    descripcion: Optional[str] = Field(None, description="Descripción general de la enfermedad")
    is_active: bool = Field(True, description="Estado activo de la enfermedad")


class EnfermedadUpdateSchema(BaseModel):
    """Schema para actualizar una enfermedad"""
    tabla: Optional[str] = Field(None, description="Tabla de referencia")
    codigo: Optional[str] = Field(None, description="Código de la enfermedad")
    nombre: Optional[str] = Field(None, description="Nombre de la enfermedad")
    descripcion: Optional[str] = Field(None, description="Descripción general de la enfermedad")
    is_active: Optional[bool] = Field(None, description="Estado activo de la enfermedad")


class EnfermedadResponseSchema(BaseModel):
    """Schema para respuesta de enfermedad"""
    id: str = Field(..., description="ID de la enfermedad")
    tabla: str = Field(..., description="Tabla de referencia")
    codigo: str = Field(..., description="Código de la enfermedad")
    nombre: str = Field(..., description="Nombre de la enfermedad")
    descripcion: Optional[str] = Field(None, description="Descripción general de la enfermedad")
    is_active: bool = Field(..., description="Estado activo de la enfermedad")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")


class EnfermedadListResponseSchema(BaseModel):
    """Schema para respuesta de lista de enfermedades"""
    enfermedades: List[EnfermedadResponseSchema] = Field(..., description="Lista de enfermedades")
    total: int = Field(..., description="Total de enfermedades")
    skip: int = Field(..., description="Número de elementos omitidos")
    limit: int = Field(..., description="Límite de elementos por página")


class EnfermedadSearchResponseSchema(BaseModel):
    """Schema para respuesta de búsqueda de enfermedades"""
    enfermedades: List[EnfermedadResponseSchema] = Field(..., description="Lista de enfermedades encontradas")
    search_term: str = Field(..., description="Término de búsqueda utilizado")
    skip: int = Field(..., description="Número de elementos omitidos")
    limit: int = Field(..., description="Límite de elementos por página")


class EnfermedadByTablaResponseSchema(BaseModel):
    """Schema para respuesta de enfermedades por tabla"""
    enfermedades: List[EnfermedadResponseSchema] = Field(..., description="Lista de enfermedades de la tabla")
    tabla: str = Field(..., description="Tabla de referencia")
    skip: int = Field(..., description="Número de elementos omitidos")
    limit: int = Field(..., description="Límite de elementos por página")


class PaginationQuerySchema(BaseModel):
    """Schema para parámetros de paginación"""
    skip: int = Field(0, ge=0, description="Número de elementos a omitir")
    limit: int = Field(100, ge=1, le=1000, description="Número máximo de elementos a retornar")


class SearchQuerySchema(PaginationQuerySchema):
    """Schema para parámetros de búsqueda"""
    q: str = Field(..., min_length=1, description="Término de búsqueda")


class TablaQuerySchema(PaginationQuerySchema):
    """Schema para parámetros de consulta por tabla"""
    tabla: str = Field(..., min_length=1, description="Tabla de referencia")
