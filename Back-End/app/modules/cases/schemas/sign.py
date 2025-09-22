from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class CaseSignRequest(BaseModel):
    """Schema para firmar un caso"""
    # Resultados existentes
    method: Optional[List[str]] = Field(None, description="Lista de métodos utilizados")
    macro_result: Optional[str] = Field(None, max_length=5000, description="Resultado macroscópico")
    micro_result: Optional[str] = Field(None, max_length=5000, description="Resultado microscópico")
    diagnosis: Optional[str] = Field(None, max_length=2000, description="Diagnóstico")
    observations: Optional[str] = Field(None, max_length=1000, description="Observaciones adicionales")
    
    # Diagnósticos CIE-10 y CIE-O
    cie10_diagnosis: Optional[Dict[str, str]] = Field(None, description="Diagnóstico CIE-10 con code y name")
    cieo_diagnosis: Optional[Dict[str, str]] = Field(None, description="Diagnóstico CIE-O con code y name")


class CaseSignResponse(BaseModel):
    """Schema de respuesta para la firma de un caso"""
    case_code: str
    state: str
    signed_at: datetime
    message: str

    class Config:
        from_attributes = True


class CaseSignValidation(BaseModel):
    """Schema para validación de firma"""
    case_code: str
    can_sign: bool
    message: str
    current_state: Optional[str] = None

    class Config:
        from_attributes = True
