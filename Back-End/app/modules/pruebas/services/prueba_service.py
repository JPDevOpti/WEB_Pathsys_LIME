from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging

from app.modules.pruebas.models.prueba import Prueba
from app.modules.pruebas.schemas.prueba import (
    PruebaCreate,
    PruebaUpdate,
    PruebaResponse,
    PruebaSearch,
    PruebasListResponse
)
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository

logger = logging.getLogger(__name__)


class PruebaService:
    """Servicio para la lógica de negocio de pruebas"""
    
    def __init__(self, repository: PruebaRepository):
        self.repository = repository
    
    async def create_prueba(self, prueba_data: PruebaCreate) -> PruebaResponse:
        """Crear una nueva prueba"""
        try:
            # Verificar que el código no exista
            existing_prueba = await self.repository.get_by_code(prueba_data.prueba_code)
            if existing_prueba:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una prueba con el código {prueba_data.prueba_code}"
                )
            
            # Crear la prueba
            prueba = await self.repository.create(prueba_data)
            logger.info(f"Prueba creada: {prueba.prueba_code}")
            
            prueba_dict = prueba.model_dump()
            prueba_dict["id"] = str(prueba_dict.get("_id", prueba_dict.get("id", "")))
            return PruebaResponse(**prueba_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando prueba: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_prueba_by_code(self, code: str) -> Optional[PruebaResponse]:
        """Obtener prueba por código"""
        try:
            prueba = await self.repository.get_by_code(code)
            if not prueba:
                return None
                
            prueba_dict = prueba.model_dump()
            prueba_dict["id"] = str(prueba_dict.get("_id", prueba_dict.get("id", "")))
            return PruebaResponse(**prueba_dict)
            
        except Exception as e:
            logger.error(f"Error obteniendo prueba por código {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_all_pruebas(self, search_params: PruebaSearch) -> PruebasListResponse:
        """Obtener todas las pruebas con filtros y paginación"""
        try:
            # Si no se especifica activo, filtrar solo activos por defecto
            if search_params.activo is None:
                search_params.activo = True
                
            pruebas = await self.repository.get_all(search_params)
            total = await self.repository.count(search_params)
            
            pruebas_response = []
            for prueba in pruebas:
                prueba_dict = prueba.model_dump()
                prueba_dict["id"] = str(prueba_dict.get("_id", prueba_dict.get("id", "")))
                pruebas_response.append(PruebaResponse(**prueba_dict))
            
            return PruebasListResponse(
                pruebas=pruebas_response,
                total=total,
                skip=search_params.skip,
                limit=search_params.limit,
                has_next=search_params.skip + len(pruebas_response) < total,
                has_prev=search_params.skip > 0
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo pruebas: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def update_prueba_by_code(self, code: str, prueba_update: PruebaUpdate) -> Optional[PruebaResponse]:
        """Actualizar una prueba por código"""
        try:
            # Verificar que la prueba existe
            existing_prueba = await self.repository.get_by_code(code)
            if not existing_prueba:
                raise HTTPException(status_code=404, detail="Prueba no encontrada")
            
            # Si se está cambiando el código, verificar que el nuevo no exista
            if prueba_update.prueba_code and prueba_update.prueba_code != code:
                code_exists = await self.repository.get_by_code(prueba_update.prueba_code)
                if code_exists:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe una prueba con el código {prueba_update.prueba_code}"
                    )
            
            # Actualizar la prueba
            updated_prueba = await self.repository.update_by_code(code, prueba_update)
            if not updated_prueba:
                raise HTTPException(status_code=404, detail="Prueba no encontrada")
            
            logger.info(f"Prueba actualizada: {code}")
            prueba_dict = updated_prueba.model_dump()
            prueba_dict["id"] = str(prueba_dict.get("_id", prueba_dict.get("id", "")))
            return PruebaResponse(**prueba_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error actualizando prueba {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def delete_prueba_by_code(self, code: str) -> bool:
        """Eliminar una prueba por código (eliminación permanente)"""
        try:
            # Verificar que la prueba existe
            existing_prueba = await self.repository.get_by_code(code)
            if not existing_prueba:
                return False
            
            # Realizar eliminación permanente
            success = await self.repository.delete_by_code(code)
            if success:
                logger.info(f"Prueba eliminada permanentemente: {code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error eliminando prueba {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def toggle_active_prueba_by_code(self, code: str) -> bool:
        """Cambiar estado activo/inactivo de una prueba por código"""
        try:
            # Verificar que la prueba existe (incluyendo inactivas)
            existing_prueba = await self.repository.get_by_code_including_inactive(code)
            if not existing_prueba:
                return False
            
            # Alternar el estado is_active
            new_active_state = not existing_prueba.is_active
            success = await self.repository.toggle_active_by_code(code, new_active_state)
            
            if success:
                estado = "activada" if new_active_state else "desactivada"
                logger.info(f"Prueba {estado}: {code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cambiando estado de prueba {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")