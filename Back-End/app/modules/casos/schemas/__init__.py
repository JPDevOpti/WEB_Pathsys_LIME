"""Esquemas para el módulo de casos"""

from .caso import (
    MuestraInfo,
    PacienteInfo,
    MedicoInfo,
    PatologoInfo,
    ResultadoInfo,
    DiagnosticoCIE10,
    DiagnosticoCIEO,
    CasoCreate,
    CasoCreateRequest,
    CasoCreateWithCode,
    CasoUpdate,
    CasoResponse,
    CasoSearch,
    CasoStats,
    MuestraStats,
    CasoDeleteResponse,
    EntidadInfo,
    # Nuevas clases para estadísticas de pruebas
    PruebaStats,
    PruebaDetails,
    PruebasReportData,
    PatologoPorPrueba
)

__all__ = [
    "MuestraInfo",
    "PacienteInfo",
    "MedicoInfo",
    "PatologoInfo",
    "ResultadoInfo",
    "DiagnosticoCIE10",
    "DiagnosticoCIEO",
    "CasoCreate",
    "CasoCreateRequest",
    "CasoCreateWithCode",
    "CasoUpdate",
    "CasoResponse",
    "CasoSearch",
    "CasoStats",
    "MuestraStats",
    "CasoDeleteResponse",
    "EntidadInfo",
    # Nuevas clases para estadísticas de pruebas
    "PruebaStats",
    "PruebaDetails",
    "PruebasReportData",
    "PatologoPorPrueba"
]