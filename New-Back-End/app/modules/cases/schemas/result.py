from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ResultUpdate(BaseModel):
    method: Optional[List[str]] = Field(None, description="Lista de métodos utilizados")
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

    class Config:
        from_attributes = True


class ResultInfo(BaseModel):
    method: Optional[List[str]] = None
    macro_result: Optional[str] = None
    micro_result: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
