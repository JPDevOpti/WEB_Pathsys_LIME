from typing import Optional, Any, List, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Respuesta estándar de la API"""
    success: bool = True
    message: str = "Operación exitosa"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada estándar"""
    success: bool = True
    message: str = "Datos obtenidos exitosamente"
    data: List[T]
    pagination: 'PaginationInfo'
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationInfo(BaseModel):
    """Información de paginación"""
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class HealthResponse(BaseModel):
    """Respuesta del health check"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2.0.0"
    database: str = "connected"
    uptime: Optional[str] = None

class StatsResponse(BaseModel):
    """Respuesta de estadísticas"""
    total_usuarios: int = 0
    total_pacientes: int = 0
    total_casos: int = 0
    total_resultados: int = 0
    casos_pendientes: int = 0
    casos_completados: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationErrorResponse(BaseModel):
    """Respuesta de error de validación"""
    success: bool = False
    message: str = "Error de validación"
    errors: List[dict]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AuthResponse(BaseModel):
    """Respuesta de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MessageResponse(BaseModel):
    """Respuesta simple con mensaje"""
    success: bool = True
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)