"""Rutas de la API para el manejo de consecutivos de casos."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository
from app.modules.casos.models.consecutivo import ConsecutivoCasoResponse
from app.config.database import get_database
from app.core.exceptions import BadRequestError

router = APIRouter(tags=["consecutivos"])


def get_consecutivo_repository(database: AsyncIOMotorDatabase = Depends(get_database)) -> ConsecutivoRepository:
    """Dependencia para el repositorio de consecutivos."""
    return ConsecutivoRepository(database)


@router.get("/", response_model=List[ConsecutivoCasoResponse])
async def listar_consecutivos(consecutivo_repo: ConsecutivoRepository = Depends(get_consecutivo_repository)):
    """Listar todos los consecutivos por año."""
    try:
        consecutivos = await consecutivo_repo.listar_todos_consecutivos()
        return [ConsecutivoCasoResponse(**consecutivo.model_dump()) for consecutivo in consecutivos]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{ano}", response_model=ConsecutivoCasoResponse)
async def obtener_consecutivo_por_ano(
    ano: int,
    consecutivo_repo: ConsecutivoRepository = Depends(get_consecutivo_repository)
):
    """Obtener consecutivo de un año específico."""
    try:
        consecutivo = await consecutivo_repo.obtener_consecutivo_por_ano(ano)
        if not consecutivo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No hay consecutivos para el año {ano}"
            )
        return ConsecutivoCasoResponse(**consecutivo.model_dump())
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{ano}/estadisticas", response_model=dict)
async def obtener_estadisticas_consecutivos(consecutivo_repo: ConsecutivoRepository = Depends(get_consecutivo_repository)):
    """Obtener estadísticas de todos los consecutivos."""
    try:
        return await consecutivo_repo.obtener_estadisticas_consecutivos()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{ano}/reset")
async def resetear_consecutivo_ano(
    ano: int,
    nuevo_numero: int = 0,
    consecutivo_repo: ConsecutivoRepository = Depends(get_consecutivo_repository)
):
    """Resetear el consecutivo de un año específico."""
    try:
        actualizado = await consecutivo_repo.resetear_consecutivo_ano(ano, nuevo_numero)
        if not actualizado:
            await consecutivo_repo.crear_consecutivo_ano(ano, nuevo_numero)
        
        return {
            "message": f"Consecutivo del año {ano} reseteado a {nuevo_numero}",
            "ano": ano,
            "nuevo_numero": nuevo_numero
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/inicializar")
async def inicializar_indices(consecutivo_repo: ConsecutivoRepository = Depends(get_consecutivo_repository)):
    """Inicializar índices de la colección de consecutivos."""
    try:
        await consecutivo_repo.inicializar_indices()
        return {"message": "Índices de consecutivos inicializados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
