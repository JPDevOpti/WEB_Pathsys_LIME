"""Modelos para el manejo de tickets de soporte."""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
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
    title: str = Field(..., max_length=100, min_length=1, description="Título del ticket")
    category: TicketCategoryEnum = Field(..., description="Categoría del ticket")
    description: str = Field(..., max_length=500, min_length=1, description="Descripción detallada")
    image: Optional[str] = Field(None, description="URL de la imagen adjunta")
    ticket_date: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del ticket")
    status: TicketStatusEnum = Field(default=TicketStatusEnum.OPEN, description="Estado actual del ticket")
    created_by: str = Field(..., description="ID del usuario que creó el ticket")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        """Validar y limpiar título."""
        if not v or not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()
    
    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        """Validar y limpiar descripción."""
        if not v or not v.strip():
            raise ValueError('La descripción no puede estar vacía')
        return v.strip()
    
    @field_validator('ticket_code')
    @classmethod
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
