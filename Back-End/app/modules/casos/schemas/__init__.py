"""Esquemas para el módulo de casos"""

from .caso import (
    MuestraInfo,
    PacienteInfo,
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
    PatologoPorPrueba,
    # Clases para notas adicionales
    NotaAdicional,
    AgregarNotaAdicionalRequest
)

__all__ = [
    "MuestraInfo",
    "PacienteInfo",
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
    "PatologoPorPrueba",
    # Clases para notas adicionales
    "NotaAdicional",
    "AgregarNotaAdicionalRequest"
]