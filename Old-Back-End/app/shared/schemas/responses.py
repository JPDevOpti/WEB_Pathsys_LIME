"""Esquemas de respuesta compartidos"""

from typing import Optional, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """Modelo de respuesta estándar"""
    success: bool = True
    message: str = "Operación exitosa"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada estándar"""
    success: bool = True
    message: str = "Datos obtenidos exitosamente"
    data: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

def create_response(data: T = None, message: str = "Operación exitosa") -> ResponseModel[T]:
    """Crear respuesta estándar"""
    return ResponseModel[T](
        success=True,
        message=message,
        data=data
    )

def create_paginated_response(
    data: List[T],
    total: int,
    skip: int,
    limit: int,
    message: str = "Datos obtenidos exitosamente"
) -> PaginatedResponse[T]:
    """Crear respuesta paginada"""
    has_next = skip + limit < total
    has_prev = skip > 0
    
    return PaginatedResponse[T](
        success=True,
        message=message,
        data=data,
        total=total,
        skip=skip,
        limit=limit,
        has_next=has_next,
        has_prev=has_prev
    )

def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Any] = None
) -> ErrorResponse:
    """Crear respuesta de error"""
    return ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        details=details
    )
