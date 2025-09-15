from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.dependencies import get_database
from app.modules.casos.repositories.management.update_repository import UpdateCaseRepository
from app.modules.casos.services.management.update_service import UpdateCaseService
from app.modules.casos.schemas.management.update import (
    UpdateCaseRequest,
    UpdateCaseResponse
)
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(prefix="/casos", tags=["Gestión de Casos - Actualización"])


def get_update_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UpdateCaseRepository:
    """Dependency para obtener el repositorio de actualización"""
    return UpdateCaseRepository(db)


def get_update_service(update_repo: UpdateCaseRepository = Depends(get_update_repository)) -> UpdateCaseService:
    """Dependency para obtener el servicio de actualización"""
    return UpdateCaseService(update_repo)


@router.put("/{caso_code}", response_model=UpdateCaseResponse, status_code=status.HTTP_200_OK)
async def update_case(
    caso_code: str,
    update_data: UpdateCaseRequest,
    update_service: UpdateCaseService = Depends(get_update_service)
) -> UpdateCaseResponse:
    """
    Actualizar un caso existente
    
    - **caso_code**: Código único del caso a actualizar
    - **update_data**: Datos a actualizar (todos los campos son opcionales)
    
    Retorna la información del caso actualizado.
    """
    try:
        return await update_service.update_case(caso_code, update_data, "sistema")
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")


@router.get("/{caso_code}/validate", status_code=status.HTTP_200_OK)
async def validate_case_exists(
    caso_code: str,
    update_repo: UpdateCaseRepository = Depends(get_update_repository)
) -> dict:
    """
    Validar que un caso existe
    
    - **caso_code**: Código único del caso a validar
    
    Retorna si el caso existe o no.
    """
    try:
        exists = await update_repo.validate_case_exists(caso_code)
        return {
            "caso_code": caso_code,
            "exists": exists,
            "message": "Caso encontrado" if exists else "Caso no encontrado"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno: {str(e)}")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check para el servicio de actualización"""
    return {
        "service": "update-cases",
        "status": "healthy",
        "message": "Servicio de actualización de casos funcionando correctamente"
    }