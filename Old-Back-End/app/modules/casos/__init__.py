"""Módulo de casos"""

from .models import (
    Caso, 
    PrioridadCasoEnum,
    TipoResultadoEnum,
    EntidadInfo,
    PatologoInfo as ModelPatologoInfo,
    DiagnosticoCIE10 as ModelDiagnosticoCIE10,
    DiagnosticoCIEO as ModelDiagnosticoCIEO,
    ResultadoInfo as ModelResultadoInfo
)
from .schemas import (
    CasoCreate,
    CasoUpdate,
    CasoResponse,
    CasoSearch,
    CasoStats,
    MuestraInfo,
    PacienteInfo,
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
    "PrioridadCasoEnum",
    "TipoResultadoEnum", 
    "EntidadInfo",
    "ModelPatologoInfo",
    "ModelDiagnosticoCIE10",
    "ModelDiagnosticoCIEO",
    "ModelResultadoInfo",
    "CasoCreate",
    "CasoUpdate",
    "CasoResponse",
    "CasoSearch",
    "CasoStats",
    "MuestraInfo",
    "PacienteInfo",
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