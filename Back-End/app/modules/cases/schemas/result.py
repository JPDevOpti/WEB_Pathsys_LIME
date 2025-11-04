from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class DiagnosisInfo(BaseModel):
    id: Optional[str] = Field(default=None, description="Identificador interno opcional")
    code: str = Field(..., description="Código del diagnóstico")
    name: str = Field(..., description="Nombre del diagnóstico")


class DiagnosisInfoLegacy(BaseModel):
    id: Optional[str] = Field(default=None, description="Identificador interno opcional")
    codigo: str = Field(..., description="Código del diagnóstico (legacy)")
    nombre: str = Field(..., description="Nombre del diagnóstico (legacy)")


class ResultUpdate(BaseModel):
    method: Optional[List[str]] = Field(None, description="Lista de métodos utilizados")
    
    @field_validator('method')
    @classmethod
    def validate_methods_not_empty(cls, v):
        if v is not None:
            # Filtrar métodos vacíos y validar que quede al menos uno
            non_empty = [m.strip() for m in v if m and m.strip()]
            if len(v) > 0 and len(non_empty) == 0:
                raise ValueError('Los métodos no pueden estar vacíos')
            return non_empty if non_empty else None
        return v
    macro_result: Optional[str] = Field(None, max_length=5000, description="Resultado macroscópico")
    micro_result: Optional[str] = Field(None, max_length=5000, description="Resultado microscópico")
    diagnosis: Optional[str] = Field(None, max_length=2000, description="Diagnóstico")
    observations: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")
    cie10_diagnosis: Optional[DiagnosisInfo] = Field(
        None, description="Diagnóstico CIE-10 en el nuevo formato"
    )
    cieo_diagnosis: Optional[DiagnosisInfo] = Field(
        None, description="Diagnóstico CIE-O en el nuevo formato"
    )
    diagnostico_cie10: Optional[DiagnosisInfoLegacy] = Field(
        None, description="Diagnóstico CIE-10 en formato legacy"
    )
    diagnostico_cieo: Optional[DiagnosisInfoLegacy] = Field(
        None, description="Diagnóstico CIE-O en formato legacy"
    )


class ResultResponse(BaseModel):
    id: str
    case_code: str
    result: Optional[dict] = None
    state: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResultInfo(BaseModel):
    method: Optional[List[str]] = None
    macro_result: Optional[str] = None
    micro_result: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None
    cie10_diagnosis: Optional[DiagnosisInfo] = None
    cieo_diagnosis: Optional[DiagnosisInfo] = None
    diagnostico_cie10: Optional[DiagnosisInfoLegacy] = None
    diagnostico_cieo: Optional[DiagnosisInfoLegacy] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
