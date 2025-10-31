from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class CaseSignRequest(BaseModel):
    """Schema para firmar un caso"""
    # Resultados existentes
    method: Optional[List[str]] = None
    macro_result: Optional[str] = None
    micro_result: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None
    
    # Diagnósticos CIE-10 y CIE-O
    cie10_diagnosis: Optional[Dict[str, str]] = None
    cieo_diagnosis: Optional[Dict[str, str]] = None


class CaseSignResponse(BaseModel):
    """Schema de respuesta para la firma de un caso"""
    case_code: str
    state: str
    signed_at: datetime
    message: str

    model_config = ConfigDict(from_attributes=True)


class CaseSignValidation(BaseModel):
    """Schema para validación de firma"""
    case_code: str
    can_sign: bool
    message: str
    current_state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
