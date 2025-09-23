from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging

from app.modules.enfermedades.repositories.enfermedad_repository import EnfermedadRepository
from app.modules.enfermedades.models.enfermedad import EnfermedadCreate, EnfermedadUpdate, EnfermedadInDB, EnfermedadResponse

logger = logging.getLogger(__name__)


class EnfermedadService:
    """Servicio para operaciones de enfermedades"""
    
    def __init__(self, repository: EnfermedadRepository):
        self.repository = repository
    
    async def create_enfermedad(self, enfermedad: EnfermedadCreate) -> EnfermedadResponse:
        """Crear una nueva enfermedad"""
        try:
            # Verificar si ya existe una enfermedad con el mismo código
            existing = await self.repository.get_by_codigo(enfermedad.codigo)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una enfermedad con el código {enfermedad.codigo}"
                )
            
            # Crear la enfermedad
            created_enfermedad = await self.repository.create(enfermedad)
            
            return EnfermedadResponse(**created_enfermedad.model_dump())
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando enfermedad: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
    async def get_enfermedad_by_id(self, enfermedad_id: str) -> Optional[EnfermedadResponse]:
        """Obtener enfermedad por ID"""
        try:
            enfermedad = await self.repository.get_by_id(enfermedad_id)
            if not enfermedad:
                return None
            
            return EnfermedadResponse(**enfermedad.model_dump())
        except Exception as e:
            logger.error(f"Error obteniendo enfermedad por ID {enfermedad_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_enfermedad_by_codigo(self, codigo: str) -> Optional[EnfermedadResponse]:
        """Obtener enfermedad por código"""
        try:
            enfermedad = await self.repository.get_by_codigo(codigo)
            if not enfermedad:
                return None
            
            return EnfermedadResponse(**enfermedad.model_dump())
        except Exception as e:
            logger.error(f"Error obteniendo enfermedad por código {codigo}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_all_enfermedades(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Obtener todas las enfermedades"""
        try:
            # Si no se especifica activo, filtrar solo activos por defecto
            if is_active is None:
                is_active = True
                
            enfermedades = await self.repository.get_all(skip, limit, is_active)
            total = await self.repository.count_total(is_active)
            
            # Convertir a EnfermedadResponse
            enfermedades_response = []
            for enfermedad in enfermedades:
                try:
                    response = EnfermedadResponse(**enfermedad.model_dump())
                    enfermedades_response.append(response)
                except Exception as e:
                    logger.error(f"Error al convertir enfermedad: {str(e)}")
                    continue
            
            return {
                "enfermedades": enfermedades_response,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": skip + len(enfermedades_response) < total,
                "has_prev": skip > 0
            }
        except Exception as e:
            logger.error(f"Error obteniendo enfermedades: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_enfermedades_by_name(
        self, 
        nombre: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Buscar enfermedades por nombre"""
        try:
            enfermedades = await self.repository.search_by_name(nombre, skip, limit)
            
            # Convertir a EnfermedadResponse
            enfermedades_response = []
            for enfermedad in enfermedades:
                try:
                    response = EnfermedadResponse(**enfermedad.model_dump())
                    enfermedades_response.append(response)
                except Exception as e:
                    logger.error(f"Error al convertir enfermedad: {str(e)}")
                    continue
            
            return {
                "enfermedades": enfermedades_response,
                "search_term": nombre,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error buscando enfermedades por nombre: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def search_enfermedades_by_codigo(
        self, 
        codigo: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Buscar enfermedades por código"""
        try:
            enfermedades = await self.repository.search_by_codigo(codigo, skip, limit)
            
            # Convertir a EnfermedadResponse
            enfermedades_response = []
            for enfermedad in enfermedades:
                try:
                    response = EnfermedadResponse(**enfermedad.model_dump())
                    enfermedades_response.append(response)
                except Exception as e:
                    logger.error(f"Error al convertir enfermedad: {str(e)}")
                    continue
            
            return {
                "enfermedades": enfermedades_response,
                "search_term": codigo,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error buscando enfermedades por código: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def get_enfermedades_by_tabla(
        self, 
        tabla: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtener enfermedades por tabla de referencia"""
        try:
            enfermedades = await self.repository.get_by_tabla(tabla, skip, limit)
            
            # Convertir a EnfermedadResponse
            enfermedades_response = []
            for enfermedad in enfermedades:
                try:
                    response = EnfermedadResponse(**enfermedad.model_dump())
                    enfermedades_response.append(response)
                except Exception as e:
                    logger.error(f"Error al convertir enfermedad: {str(e)}")
                    continue
            
            return {
                "enfermedades": enfermedades_response,
                "tabla": tabla,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error obteniendo enfermedades de tabla {tabla}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def update_enfermedad(
        self, 
        enfermedad_id: str, 
        enfermedad_update: EnfermedadUpdate
    ) -> Optional[EnfermedadResponse]:
        """Actualizar una enfermedad"""
        try:
            # Verificar si la enfermedad existe
            existing = await self.repository.get_by_id(enfermedad_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
            
            # Si se está actualizando el código, verificar que no exista otro con el mismo código
            if enfermedad_update.codigo and enfermedad_update.codigo != existing.codigo:
                existing_by_codigo = await self.repository.get_by_codigo(enfermedad_update.codigo)
                if existing_by_codigo:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ya existe una enfermedad con el código {enfermedad_update.codigo}"
                    )
            
            # Actualizar la enfermedad
            updated_enfermedad = await self.repository.update(enfermedad_id, enfermedad_update)
            
            if not updated_enfermedad:
                raise HTTPException(status_code=500, detail="Error al actualizar la enfermedad")
            
            return EnfermedadResponse(**updated_enfermedad.model_dump())
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error actualizando enfermedad {enfermedad_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def delete_enfermedad(self, enfermedad_id: str) -> bool:
        """Eliminar una enfermedad (soft delete)"""
        try:
            # Verificar si la enfermedad existe
            existing = await self.repository.get_by_id(enfermedad_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
            
            # Eliminar la enfermedad
            success = await self.repository.delete(enfermedad_id)
            
            if not success:
                raise HTTPException(status_code=500, detail="Error al eliminar la enfermedad")
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error eliminando enfermedad {enfermedad_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    async def hard_delete_enfermedad(self, enfermedad_id: str) -> bool:
        """Eliminar una enfermedad permanentemente"""
        try:
            # Verificar si la enfermedad existe
            existing = await self.repository.get_by_id(enfermedad_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Enfermedad no encontrada")
            
            # Eliminar la enfermedad permanentemente
            success = await self.repository.hard_delete(enfermedad_id)
            
            if not success:
                raise HTTPException(status_code=500, detail="Error al eliminar la enfermedad")
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error eliminando permanentemente enfermedad {enfermedad_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
