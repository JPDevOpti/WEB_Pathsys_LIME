from typing import Optional, List, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class SortField(BaseModel):
    """Campo de ordenamiento"""
    campo: str
    direccion: str = Field(..., pattern="^(asc|desc)$")


class PageRequest(BaseModel):
    """Solicitud de paginación"""
    pagina: int = Field(1, ge=1)
    tamaño: int = Field(10, ge=1, le=100)
    ordenar_por: Optional[List[SortField]] = None


class PageResponse(BaseModel, Generic[T]):
    """Respuesta paginada"""
    datos: List[T]
    pagina_actual: int
    total_paginas: int
    total_elementos: int
    tamaño_pagina: int
    tiene_siguiente: bool
    tiene_anterior: bool


class PaginationInfo(BaseModel):
    """Información de paginación"""
    pagina_actual: int
    total_paginas: int
    total_elementos: int
    tamaño_pagina: int
    tiene_siguiente: bool
    tiene_anterior: bool