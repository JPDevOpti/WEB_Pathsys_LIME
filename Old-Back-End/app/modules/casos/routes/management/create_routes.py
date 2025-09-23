from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_database
from app.modules.casos.repositories.management.create_repository import CreateCaseRepository
from app.modules.casos.services.management.create_service import CreateCaseService
from app.modules.casos.schemas.management.create import CreateCaseRequest, CreateCaseResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

# Router para operaciones de creación de casos
router = APIRouter(prefix="/casos", tags=["casos-management-create"])


def get_create_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> CreateCaseRepository:
    """Dependencia para obtener el repositorio de creación de casos."""
    return CreateCaseRepository(db)


def get_create_service(create_repo: CreateCaseRepository = Depends(get_create_repository)) -> CreateCaseService:
    """Dependencia para obtener el servicio de creación de casos."""
    return CreateCaseService(create_repo)


@router.post("", response_model=CreateCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CreateCaseRequest,
    create_service: CreateCaseService = Depends(get_create_service)
) -> CreateCaseResponse:
    """
    Crea un nuevo caso médico en el sistema.
    
    Este endpoint permite crear un nuevo caso con toda la información necesaria:
    - Datos del paciente
    - Información médica (médico solicitante, servicio)
    - Muestras y pruebas a realizar
    - Estado y prioridad del caso
    
    Args:
        case_data: Datos del caso a crear
        
    Returns:
        CreateCaseResponse: Respuesta con información del caso creado
        
    Raises:
        HTTPException: Si hay errores de validación o creación
    """
    try:
        logger.info(f"Iniciando creación de caso para paciente: {case_data.paciente.paciente_code}")
        
        # Crear el caso usando el servicio optimizado
        result = await create_service.create_case(case_data)
        
        if not result.success:
            logger.error(f"Error al crear caso: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        logger.info(f"Caso creado exitosamente: {result.caso_code}")
        return result
        
    except ValueError as e:
        logger.warning(f"Error de validación al crear caso: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Error interno al crear caso: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al crear el caso"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint de salud para verificar que el servicio de creación está funcionando.
    """
    return {
        "status": "healthy",
        "service": "casos-management-create",
        "message": "Servicio de creación de casos funcionando correctamente"
    }
