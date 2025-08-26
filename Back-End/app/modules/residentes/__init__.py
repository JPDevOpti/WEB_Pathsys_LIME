# Módulo de Residentes

# Router
from .routes.residente_routes import router

# Modelo
from .models.residente import Residente

# Esquemas
from .schemas.residente import (
    ResidenteCreate,
    ResidenteUpdate,
    ResidenteResponse,
    ResidenteSearch,
    ResidenteEstadoUpdate
)

# Servicios
from .services.residente_service import ResidenteService

# Repositorios
from .repositories import ResidenteRepository

__all__ = [
    "router",
    "Residente",
    "ResidenteCreate",
    "ResidenteUpdate",
    "ResidenteResponse",
    "ResidenteSearch",
    "ResidenteEstadoUpdate",
    "ResidenteService",
    "ResidenteRepository"
]