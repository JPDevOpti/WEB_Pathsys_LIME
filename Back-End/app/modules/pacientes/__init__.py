"""Módulo de pacientes"""

from .models import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteSearch,
    Sexo,
    TipoAtencion
)
from .services import (
    PacienteService,
    get_paciente_service
)
from .routes import router

__all__ = [
    # Modelos
    "PacienteCreate",
    "PacienteUpdate",
    "PacienteResponse",
    "PacienteSearch",
    
    # Enumeraciones
    "Sexo",
    "TipoAtencion",
    
    # Servicios
    "PacienteService",
    "get_paciente_service",
    
    # Router
    "router"
]