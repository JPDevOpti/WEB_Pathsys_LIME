"""Esquemas del módulo de pacientes"""

from .paciente import (
    Sexo,
    TipoAtencion,
    PacienteBase,
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteSearch,
    PacienteStats
)

__all__ = [
    "Sexo",
    "TipoAtencion",
    "PacienteBase",
    "PacienteCreate",
    "PacienteUpdate",
    "PacienteResponse",
    "PacienteSearch",
    "PacienteStats"
]


