"""Modelos para el manejo de consecutivos de casos."""

from datetime import datetime
from pydantic import BaseModel, Field, validator


class ConsecutivoCaso(BaseModel):
    """Control de consecutivos de casos por año."""
    
    ano: int = Field(..., ge=2000, le=2100)
    ultimo_numero: int = Field(default=0, ge=0)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('ano')
    def validate_ano(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 5:
            raise ValueError(f'Año debe estar entre 2000 y {current_year + 5}')
        return v

    @validator('ultimo_numero')
    def validate_ultimo_numero(cls, v):
        if v < 0:
            raise ValueError('El último número no puede ser negativo')
        if v > 999999:  # Límite razonable para casos por año
            raise ValueError('El último número excede el límite permitido')
        return v


class ConsecutivoCasoCreate(BaseModel):
    """Schema para crear un nuevo control de consecutivo."""
    ano: int = Field(..., ge=2000, le=2100)
    ultimo_numero: int = Field(default=0, ge=0)


class ConsecutivoCasoResponse(BaseModel):
    """Schema de respuesta para consecutivos."""
    ano: int
    ultimo_numero: int
    fecha_actualizacion: datetime
