"""Esquemas Pydantic para la API de tickets."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.modules.tickets.models.ticket import TicketCategoryEnum, TicketStatusEnum


class TicketCreate(BaseModel):
    """Esquema para crear un nuevo ticket."""
    titulo: str = Field(..., max_length=100, min_length=1, description="Título del ticket")
    categoria: TicketCategoryEnum = Field(..., description="Categoría del ticket")
    descripcion: str = Field(..., max_length=500, min_length=1, description="Descripción detallada")
    imagen: Optional[str] = Field(None, description="URL de la imagen adjunta")

    @validator('titulo', pre=True)
    def validate_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

    @validator('descripcion', pre=True)
    def validate_descripcion(cls, v):
        if not v or not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()

    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    """Esquema para actualizar un ticket."""
    titulo: Optional[str] = Field(None, max_length=100, min_length=1)
    categoria: Optional[TicketCategoryEnum] = None
    descripcion: Optional[str] = Field(None, max_length=500, min_length=1)
    imagen: Optional[str] = None
    estado: Optional[TicketStatusEnum] = None

    @validator('titulo', pre=True)
    def validate_titulo(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('El título no puede estar vacío')
        return v.strip() if v else v

    @validator('descripcion', pre=True)
    def validate_descripcion(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('La descripción no puede estar vacía')
        return v.strip() if v else v

    class Config:
        from_attributes = True


class TicketSearch(BaseModel):
    """Esquema para búsqueda y filtros de tickets."""
    estado: Optional[TicketStatusEnum] = None
    categoria: Optional[TicketCategoryEnum] = None
    created_by: Optional[str] = None
    search_text: Optional[str] = Field(None, description="Buscar en título y descripción")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    """Esquema para cambiar solo el estado de un ticket."""
    estado: TicketStatusEnum = Field(..., description="Nuevo estado del ticket")

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Esquema de respuesta completa de un ticket."""
    ticket_code: str = Field(..., description="Código único del ticket")
    titulo: str = Field(..., description="Título del ticket")
    categoria: TicketCategoryEnum = Field(..., description="Categoría del ticket")
    descripcion: str = Field(..., description="Descripción detallada")
    imagen: Optional[str] = Field(None, description="URL de la imagen adjunta")
    fecha_ticket: datetime = Field(..., description="Fecha de creación del ticket")
    estado: TicketStatusEnum = Field(..., description="Estado actual del ticket")
    created_by: Optional[str] = Field(None, description="ID del usuario que creó el ticket")

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Esquema de respuesta compacta para listas de tickets."""
    ticket_code: str = Field(..., description="Código único del ticket")
    titulo: str = Field(..., description="Título del ticket")
    categoria: TicketCategoryEnum = Field(..., description="Categoría del ticket")
    descripcion: str = Field(..., description="Descripción resumida del ticket")
    estado: TicketStatusEnum = Field(..., description="Estado actual del ticket")
    imagen: Optional[str] = Field(None, description="URL de la imagen adjunta")
    fecha_ticket: datetime = Field(..., description="Fecha de creación del ticket")

    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    """Esquema de respuesta para upload de imagen."""
    image_url: str = Field(..., description="URL de la imagen subida")
    mensaje: str = Field(..., description="Mensaje de confirmación")

    class Config:
        from_attributes = True
