from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.schemas.sign import CaseSignRequest, CaseSignResponse, CaseSignValidation
from app.modules.cases.schemas.case import CaseResponse
from app.modules.cases.services.sign_service import SignService
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(tags=["sign"])


def get_sign_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> SignService:
    return SignService(db)


@router.put("/{case_code}/sign", response_model=CaseResponse)
async def sign_case(
    case_code: str, 
    payload: CaseSignRequest, 
    service: SignService = Depends(get_sign_service)
):
    """
    Firmar un caso cambiando su estado de 'Por firmar' a 'Por entregar'
    
    - **case_code**: Código del caso (ej: 2025-00001)
    - **method**: Lista de métodos utilizados (opcional)
    - **macro_result**: Resultado macroscópico (opcional)
    - **micro_result**: Resultado microscópico (opcional)
    - **diagnosis**: Diagnóstico (opcional)
    - **observations**: Observaciones adicionales (opcional)
    - **cie10_diagnosis**: Diagnóstico CIE-10 con code y name (opcional)
    - **cieo_diagnosis**: Diagnóstico CIE-O con code y name (opcional)
    
    Solo se pueden firmar casos en estado 'Por firmar'
    """
    try:
        return await service.sign_case(case_code, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{case_code}/sign/validation", response_model=CaseSignValidation)
async def validate_case_for_signing(
    case_code: str, 
    service: SignService = Depends(get_sign_service)
):
    """
    Validar si un caso puede ser firmado
    
    - **case_code**: Código del caso (ej: 2025-00001)
    
    Retorna información sobre si el caso puede ser firmado basado en su estado
    """
    try:
        return await service.validate_case_for_signing(case_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
