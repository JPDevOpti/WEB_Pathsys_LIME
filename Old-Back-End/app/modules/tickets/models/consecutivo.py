"""Modelos para el manejo de consecutivos de tickets."""

from datetime import datetime
from pydantic import BaseModel, Field, validator


class ConsecutivoTicket(BaseModel):
    """Control de consecutivos de tickets por año."""
    
    year: int = Field(..., ge=2000, le=2100)
    last_number: int = Field(default=0, ge=0)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 5:
            raise ValueError(f'Año debe estar entre 2000 y {current_year + 5}')
        return v

    @validator('last_number')
    def validate_last_number(cls, v):
        if v < 0:
            raise ValueError('El último número no puede ser negativo')
        if v > 999999:
            raise ValueError('El último número excede el límite permitido')
        return v


class ConsecutivoTicketCreate(BaseModel):
    """Schema para crear un nuevo control de consecutivo."""
    year: int = Field(..., ge=2000, le=2100)
    last_number: int = Field(default=0, ge=0)
