"""Esquemas para gestión de casos"""

from .create import (
    CreateCaseRequest,
    CreateCaseResponse,
    CreatedCaseInfo,
    PatientInfo,
    EntityInfo,
    Subsample,
    SubsampleTest,
    PatientSex,
    AttentionType,
    CasePriority,
    CaseState
)

from .update import (
    UpdateCaseRequest,
    UpdateCaseResponse,
    UpdatedCaseInfo
)


__all__ = [
    # Create schemas
    "CreateCaseRequest",
    "CreateCaseResponse", 
    "CreatedCaseInfo",
    "PatientInfo",
    "EntityInfo",
    "Subsample",
    "SubsampleTest",
    "PatientSex",
    "AttentionType",
    "CasePriority",
    "CaseState",
    
    # Update schemas
    "UpdateCaseRequest",
    "UpdateCaseResponse",
    "UpdatedCaseInfo"
]
