from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging

from app.modules.entidades.models.entidad import (
    Entidad,
    EntidadCreate,
    EntidadUpdate,
    EntidadResponse,
    EntidadSearch
)
from app.modules.entidades.repositories.entidad_repository import EntidadRepository

logger = logging.getLogger(__name__)


class EntidadService:
    """Servicio para la lógica de negocio de entidades"""
    
    def __init__(self, repository: EntidadRepository):
        self.repository = repository
    
    async def create_entidad(self, entidad_data: EntidadCreate) -> EntidadResponse:
        """Crear una nueva entidad"""
        try:
            # Verificar que el código no exista
            existing_entidad = await self.repository.get_by_code_including_inactive(entidad_data.EntidadCode)
            if existing_entidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una entidad con el código {entidad_data.EntidadCode}"
                )
            
            # Crear la entidad
            entidad = await self.repository.create(entidad_data)
            logger.info(f"Entidad creada: {entidad.EntidadCode}")
            
            return EntidadResponse(**entidad.model_dump())
            
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            logger.error(f"Error creando entidad: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_entidad_by_code(self, code: str) -> Optional[EntidadResponse]:
        """Obtener entidad por código"""
        try:
            entidad = await self.repository.get_by_code(code)
            if not entidad:
                return None
                
            return EntidadResponse(**entidad.model_dump())
            
        except Exception as e:
            logger.error(f"Error obteniendo entidad por código {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def get_all_entidades(self, search_params: EntidadSearch) -> Dict[str, Any]:
        """Obtener todas las entidades con filtros y paginación"""
        try:
            # Si no se especifica activo, filtrar solo activos por defecto
            if search_params.activo is None:
                search_params.activo = True
                
            entidades = await self.repository.get_all(search_params)
            total = await self.repository.count(search_params)
            
            entidades_response = [EntidadResponse(**entidad.model_dump()) for entidad in entidades]
            
            return {
                "entidades": entidades_response,
                "total": total,
                "skip": search_params.skip,
                "limit": search_params.limit,
                "has_next": search_params.skip + len(entidades_response) < total,
                "has_prev": search_params.skip > 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo entidades: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def update_entidad_by_code(self, code: str, entidad_update: EntidadUpdate) -> Optional[EntidadResponse]:
        """Actualizar una entidad por código"""
        try:
            # Verificar que la entidad existe
            existing_entidad = await self.repository.get_by_code(code)
            if not existing_entidad:
                raise HTTPException(status_code=404, detail="Entidad no encontrada")
            
            # Si se está cambiando el código, verificar que el nuevo no exista
            if entidad_update.EntidadCode and entidad_update.EntidadCode != code:
                code_exists = await self.repository.get_by_code_including_inactive(entidad_update.EntidadCode)
                if code_exists:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe una entidad con el código {entidad_update.EntidadCode}"
                    )
            
            # Actualizar la entidad
            updated_entidad = await self.repository.update_by_code(code, entidad_update)
            if not updated_entidad:
                raise HTTPException(status_code=404, detail="Entidad no encontrada")
            
            logger.info(f"Entidad actualizada: {code}")
            return EntidadResponse(**updated_entidad.model_dump())
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error actualizando entidad {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def delete_entidad_by_code(self, code: str) -> bool:
        """Eliminar una entidad por código (eliminación permanente)"""
        try:
            # Verificar que la entidad existe
            existing_entidad = await self.repository.get_by_code_including_inactive(code)
            if not existing_entidad:
                return False
            
            # Realizar eliminación permanente
            success = await self.repository.delete_by_code(code)
            if success:
                logger.info(f"Entidad eliminada permanentemente: {code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error eliminando entidad {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    async def toggle_active_entidad_by_code(self, code: str) -> bool:
        """Cambiar estado activo/inactivo de una entidad por código"""
        try:
            # Verificar que la entidad existe (incluyendo inactivas)
            existing_entidad = await self.repository.get_by_code_including_inactive(code)
            if not existing_entidad:
                return False
            
            # Alternar el estado isActive
            new_active_state = not existing_entidad.isActive
            success = await self.repository.toggle_active_by_code(code, new_active_state)
            
            if success:
                estado = "activada" if new_active_state else "desactivada"
                logger.info(f"Entidad {estado}: {code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cambiando estado de entidad {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor") 