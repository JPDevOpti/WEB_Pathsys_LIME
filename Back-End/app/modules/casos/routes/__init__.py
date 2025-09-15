"""Rutas para el módulo de casos"""

from .caso_routes import router
from .management.create_routes import router as create_router
from .management.update_routes import router as update_router

__all__ = ["router", "create_router", "update_router"]