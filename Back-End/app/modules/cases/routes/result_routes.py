from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.schemas.result import ResultUpdate, ResultResponse
from app.modules.cases.schemas.case import CaseResponse
from app.modules.cases.services.result_service import ResultService
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(tags=["results"])


def get_result_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ResultService:
    return ResultService(db)


@router.put("/{case_code}/result", response_model=CaseResponse)
async def update_case_result(
    case_code: str, 
    payload: ResultUpdate, 
    service: ResultService = Depends(get_result_service)
):
    """
    Actualizar resultado de un caso
    
    - **case_code**: Código del caso (ej: 2025-00001)
    - **method**: Lista de métodos utilizados (opcional)
    - **macro_result**: Resultado macroscópico (opcional)
    - **micro_result**: Resultado microscópico (opcional)
    - **diagnosis**: Diagnóstico (opcional)
    - **observations**: Observaciones adicionales (opcional)
    
    Solo se pueden editar casos con estado 'En proceso' o 'Por firmar'
    """
    try:
        return await service.update_case_result(case_code, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{case_code}/result")
async def get_case_result(
    case_code: str, 
    service: ResultService = Depends(get_result_service)
):
    """
    Obtener resultado de un caso
    
    - **case_code**: Código del caso (ej: 2025-00001)
    
    Retorna el resultado del caso si existe
    """
    try:
        result = await service.get_case_result(case_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"Caso con código {case_code} no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.get("/{case_code}/result/validation")
async def validate_case_for_editing(
    case_code: str, 
    service: ResultService = Depends(get_result_service)
):
    """
    Validar si un caso puede ser editado
    
    - **case_code**: Código del caso (ej: 2025-00001)
    
    Retorna si el caso puede ser editado basado en su estado
    """
    try:
        can_edit = await service.validate_case_state_for_editing(case_code)
        return {
            "case_code": case_code,
            "can_edit": can_edit,
            "message": "El caso puede ser editado" if can_edit else "El caso no puede ser editado debido a su estado"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
