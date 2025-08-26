"""Módulo de casos"""

from .models import Caso
from .schemas import (
    CasoCreate,
    CasoUpdate,
    CasoResponse,
    CasoSearch,
    CasoStats,
    MuestraInfo,
    PacienteInfo,
    MedicoInfo,
    PatologoInfo,
    ResultadoInfo,
    DiagnosticoCIE10,
    DiagnosticoCIEO,
    PruebaStats,
    PruebaDetails,
    PruebasReportData,
    PatologoPorPrueba
)
from .repositories import CasoRepository
from .services import CasoService
from .routes import router

__all__ = [
    "Caso",
    "CasoCreate",
    "CasoUpdate",
    "CasoResponse",
    "CasoSearch",
    "CasoStats",
    "MuestraInfo",
    "PacienteInfo",
    "MedicoInfo",
    "PatologoInfo",
    "ResultadoInfo",
    "DiagnosticoCIE10",
    "DiagnosticoCIEO",
    "PruebaStats",
    "PruebaDetails",
    "PruebasReportData",
    "PatologoPorPrueba",
    "CasoRepository",
    "CasoService",
    "router"
]