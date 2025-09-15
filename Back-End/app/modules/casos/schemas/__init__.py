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

# Importar esquemas de gestión modular
from .management import (
    # Create schemas
    CreateCaseRequest,
    CreateCaseResponse,
    CreatedCaseInfo,
    PatientInfo as ManagementPatientInfo,
    EntityInfo as ManagementEntityInfo,
    Subsample,
    SubsampleTest,
    PatientSex,
    AttentionType,
    CasePriority,
    CaseState,
    
    # Update schemas
    UpdateCaseRequest,
    UpdateCaseResponse,
    UpdatedCaseInfo
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
    "AgregarNotaAdicionalRequest",
    
    # Esquemas de gestión modular
    "CreateCaseRequest",
    "CreateCaseResponse",
    "CreatedCaseInfo",
    "ManagementPatientInfo",
    "ManagementEntityInfo",
    "Subsample",
    "SubsampleTest",
    "PatientSex",
    "AttentionType",
    "CasePriority",
    "CaseState",
    "UpdateCaseRequest",
    "UpdateCaseResponse",
    "UpdatedCaseInfo"
]