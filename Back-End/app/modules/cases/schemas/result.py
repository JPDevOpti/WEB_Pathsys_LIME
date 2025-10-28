from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


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
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
