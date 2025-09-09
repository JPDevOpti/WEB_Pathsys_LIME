"""Modelos para el manejo de tickets de soporte."""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from app.shared.models.base import PyObjectId


class TicketCategoryEnum(str, Enum):
    """Categorías de tickets disponibles."""
    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    TECHNICAL = "technical"


class TicketStatusEnum(str, Enum):
    """Estados de tickets disponibles."""
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(BaseModel):
    """Modelo principal de Ticket para MongoDB."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    ticket_code: str = Field(..., max_length=50, description="Código único del ticket (T-YYYY-NNN)")
    titulo: str = Field(..., max_length=100, min_length=1, description="Título del ticket")
    categoria: TicketCategoryEnum = Field(..., description="Categoría del ticket")
    descripcion: str = Field(..., max_length=500, min_length=1, description="Descripción detallada")
    imagen: Optional[str] = Field(None, description="URL de la imagen adjunta")
    fecha_ticket: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del ticket")
    estado: TicketStatusEnum = Field(default=TicketStatusEnum.OPEN, description="Estado actual del ticket")
    created_by: str = Field(..., description="ID del usuario que creó el ticket")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('titulo', pre=True)
    def validate_titulo(cls, v):
        """Validar y limpiar título."""
        if not v or not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()
    
    @validator('descripcion', pre=True)
    def validate_descripcion(cls, v):
        """Validar y limpiar descripción."""
        if not v or not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()
    
    @validator('ticket_code')
    def validate_ticket_code(cls, v):
        """Validar formato del código de ticket (T-YYYY-NNN)."""
        if not v:
            raise ValueError('El código de ticket es requerido')
        
        # Validar formato T-YYYY-NNN
        parts = v.split('-')
        if len(parts) != 3 or parts[0] != 'T':
            raise ValueError('El código debe tener formato T-YYYY-NNN')
        
        try:
            year = int(parts[1])
            number = int(parts[2])
            if year < 2000 or year > 2100:
                raise ValueError('Año debe estar entre 2000 y 2100')
            if number < 1 or number > 999999:
                raise ValueError('Número consecutivo inválido')
        except ValueError:
            raise ValueError('Formato de código inválido')
        
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True
