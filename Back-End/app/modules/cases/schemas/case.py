from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class EntityInfo(BaseModel):
    id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)


class PatientInfo(BaseModel):
    patient_code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., max_length=20)
    entity_info: EntityInfo
    care_type: str = Field(..., max_length=50)
    observations: Optional[str] = Field(None, max_length=1000)


class SampleTest(BaseModel):
    id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    quantity: int = Field(default=1, ge=1)


class SampleInfo(BaseModel):
    body_region: str = Field(..., max_length=100)
    tests: List[SampleTest] = Field(default_factory=list)


class AssignedPathologist(BaseModel):
    id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)


class CasePriority(str):
    NORMAL = "Normal"
    PRIORITARIO = "Prioritario"


class CaseState(str):
    EN_PROCESO = "En proceso"
    POR_FIRMAR = "Por firmar"
    POR_ENTREGAR = "Por entregar"
    COMPLETADO = "Completado"


class AdditionalNote(BaseModel):
    date: datetime = Field(..., description="Fecha de la nota")
    note: str = Field(..., max_length=1000, description="Contenido de la nota")
    
    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    patient_info: PatientInfo
    requesting_physician: Optional[str] = Field(None, max_length=200)
    service: Optional[str] = Field(None, max_length=100)
    samples: Optional[List[SampleInfo]] = Field(default_factory=list)
    state: str = Field(default=CaseState.EN_PROCESO)
    priority: str = Field(default=CasePriority.NORMAL)
    observations: Optional[str] = Field(None, max_length=1000)


class CaseUpdate(BaseModel):
    patient_info: Optional[PatientInfo] = None
    requesting_physician: Optional[str] = Field(None, max_length=200)
    service: Optional[str] = Field(None, max_length=100)
    samples: Optional[List[SampleInfo]] = None
    state: Optional[str] = None
    priority: Optional[str] = None
    observations: Optional[str] = Field(None, max_length=1000)
    assigned_pathologist: Optional[AssignedPathologist] = None
    delivered_to: Optional[str] = Field(None, max_length=200)
    delivered_at: Optional[datetime] = None
    business_days: Optional[int] = Field(None, ge=0, description="Business days elapsed")
    additional_notes: Optional[List[AdditionalNote]] = None


class CaseResult(BaseModel):
    method: Optional[List[str]] = None
    macro_result: Optional[str] = None
    micro_result: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None
    cie10_diagnosis: Optional[Dict[str, str]] = None
    cieo_diagnosis: Optional[Dict[str, str]] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CaseResponse(BaseModel):
    id: str
    case_code: str
    patient_info: PatientInfo
    requesting_physician: Optional[str] = None
    service: Optional[str] = None
    samples: List[SampleInfo] = Field(default_factory=list)
    state: str
    priority: str
    observations: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    signed_at: Optional[datetime] = None
    assigned_pathologist: Optional[AssignedPathologist] = None
    result: Optional[CaseResult] = None
    delivered_to: Optional[str] = None
    delivered_at: Optional[datetime] = None
    business_days: Optional[int] = None
    additional_notes: Optional[List[AdditionalNote]] = None

    class Config:
        from_attributes = True


