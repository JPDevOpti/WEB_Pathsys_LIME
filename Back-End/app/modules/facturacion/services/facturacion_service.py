import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId

from app.modules.facturacion.repositories.facturacion_repository import FacturacionRepository
from app.modules.facturacion.models.facturacion import Facturacion
from app.modules.facturacion.schemas.facturacion import (
    FacturacionCreate,
    FacturacionUpdate,
    FacturacionResponse,
    FacturacionSearch
)
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ConflictError
)
from app.shared.services.user_management import UserManagementService

logger = logging.getLogger(__name__)

class FacturacionService:
    """Servicio para la lógica de negocio de Facturación"""
    
    def __init__(self, facturacion_repository: FacturacionRepository, user_management_service: UserManagementService):
        self.facturacion_repository = facturacion_repository
        self.user_management_service = user_management_service
    
    async def create_facturacion(self, facturacion_data: FacturacionCreate) -> FacturacionResponse:
        """Crear un nuevo usuario de facturación y su usuario correspondiente"""
        existing_email = await self.facturacion_repository.get_by_email(facturacion_data.facturacion_email)
        if existing_email:
            raise ConflictError("El email ya está registrado en facturación")
        
        email_exists_in_users = await self.user_management_service.check_email_exists_in_users(facturacion_data.facturacion_email)
        if email_exists_in_users:
            raise ConflictError("El email ya está registrado en usuarios")
        
        existing_codigo = await self.facturacion_repository.get_by_codigo(facturacion_data.facturacion_code)
        if existing_codigo:
            raise ConflictError("El código ya está registrado")
        
        password = facturacion_data.password
        
        facturacion = None
        user = None
        
        try:
            facturacion = await self.facturacion_repository.create_facturacion_from_schema(facturacion_data)
            
            user = await self.user_management_service.create_user_for_facturacion(
                name=facturacion_data.facturacion_name,
                email=facturacion_data.facturacion_email,
                password=password,
                is_active=facturacion_data.is_active
            )
            
            return self._to_response(facturacion)
            
        except Exception as e:
            if facturacion and not user:
                try:
                    await self.facturacion_repository.delete(str(facturacion.id))
                except:
                    pass
            
            if user and not facturacion:
                try:
                    await self.user_management_service.delete_user_by_email(facturacion_data.facturacion_email)
                except:
                    pass
            
            if "email ya está registrado" in str(e) or "Ya existe un usuario con el email" in str(e):
                raise ConflictError(str(e))
            else:
                raise BadRequestError(f"Error al crear usuario de facturación: {str(e)}")
    
    async def get_facturacion(self, facturacion_code: str) -> FacturacionResponse:
        """Obtener un usuario de facturación por código"""
        facturacion = await self.facturacion_repository.get_by_codigo(facturacion_code)
        if not facturacion:
            raise NotFoundError("Usuario de facturación no encontrado")
        return self._to_response(facturacion)
    
    async def get_facturacion_list(self, skip: int = 0, limit: int = 10) -> List[FacturacionResponse]:
        """Obtener lista de usuarios de facturación activos con paginación"""
        facturacion_list = await self.facturacion_repository.get_multi(
            filters={"is_active": True},
            skip=skip,
            limit=limit
        )
        return [self._to_response(facturacion) for facturacion in facturacion_list]
    
    async def update_facturacion(self, facturacion_code: str, facturacion_data: FacturacionUpdate) -> FacturacionResponse:
        """Actualizar un usuario de facturación"""
        existing_facturacion = await self.facturacion_repository.get_by_codigo(facturacion_code)
        if not existing_facturacion:
            raise NotFoundError("Usuario de facturación no encontrado")
        
        if facturacion_data.facturacion_email and facturacion_data.facturacion_email != existing_facturacion.facturacion_email:
            email_exists = await self.facturacion_repository.exists_by_email(
                facturacion_data.facturacion_email, 
                exclude_id=ObjectId(existing_facturacion.id)
            )
            if email_exists:
                raise ConflictError("El email ya está registrado")
        
        if facturacion_data.facturacion_code and facturacion_data.facturacion_code != existing_facturacion.facturacion_code:
            codigo_exists = await self.facturacion_repository.exists_by_codigo(
                facturacion_data.facturacion_code,
                exclude_id=ObjectId(existing_facturacion.id)
            )
            if codigo_exists:
                raise ConflictError("El código ya está registrado")
        
        try:
            updated_facturacion = await self.facturacion_repository.update(str(existing_facturacion.id), facturacion_data)
            if updated_facturacion is None:
                raise NotFoundError(f"No se pudo actualizar el usuario de facturación con código {facturacion_code}")

            try:
                final_name = getattr(updated_facturacion, 'facturacion_name', None) or facturacion_data.facturacion_name or existing_facturacion.facturacion_name
                final_email = getattr(updated_facturacion, 'facturacion_email', None) or facturacion_data.facturacion_email or existing_facturacion.facturacion_email
                final_is_active = getattr(updated_facturacion, 'is_active', None)
                if final_is_active is None:
                    final_is_active = facturacion_data.is_active if facturacion_data.is_active is not None else existing_facturacion.is_active

                await self.user_management_service.update_user_for_facturacion(
                    existing_facturacion.facturacion_email,
                    name=final_name,
                    new_email=final_email,
                    is_active=final_is_active,
                    new_password=(facturacion_data.password if hasattr(facturacion_data, 'password') else None)
                )
            except Exception as sync_error:
                logger.warning(f"Falló sincronización con usuarios para facturación {facturacion_code}: {sync_error}")

            return self._to_response(updated_facturacion)
        except Exception as e:
            raise BadRequestError(f"Error al actualizar el usuario de facturación: {str(e)}")
    
    async def delete_facturacion(self, facturacion_code: str) -> bool:
        """Eliminar permanentemente un usuario de facturación"""
        facturacion = await self.facturacion_repository.get_by_codigo(facturacion_code)
        if not facturacion:
            raise NotFoundError("Usuario de facturación no encontrado")
        
        return await self.facturacion_repository.hard_delete_by_codigo(facturacion_code)
    
    async def activate_facturacion(self, facturacion_code: str) -> FacturacionResponse:
        """Activar un usuario de facturación"""
        facturacion = await self.facturacion_repository.get_by_codigo(facturacion_code)
        if not facturacion:
            raise NotFoundError("Usuario de facturación no encontrado")
        
        if facturacion.is_active:
            raise BadRequestError("El usuario de facturación ya está activo")
        
        success = await self.facturacion_repository.activate_by_codigo(facturacion_code)
        if not success:
            raise BadRequestError("No se pudo activar el usuario de facturación")
        
        updated_facturacion = await self.facturacion_repository.get_by_codigo(facturacion_code)
        if updated_facturacion is None:
            raise NotFoundError(f"No se pudo obtener el usuario de facturación activado con código {facturacion_code}")
        return self._to_response(updated_facturacion)
    
    async def search_facturacion(self, search_params: FacturacionSearch) -> List[FacturacionResponse]:
        """Buscar usuarios de facturación con filtros"""
        facturacion_list = await self.facturacion_repository.search_facturacion(search_params)
        return [self._to_response(facturacion) for facturacion in facturacion_list]

    async def search_active_facturacion(self, search_params: FacturacionSearch) -> List[FacturacionResponse]:
        """Buscar solo usuarios de facturación activos con filtros"""
        facturacion_list = await self.facturacion_repository.search_active_facturacion(search_params)
        return [self._to_response(facturacion) for facturacion in facturacion_list]

    async def search_all_facturacion_including_inactive(self, search_params: FacturacionSearch) -> List[FacturacionResponse]:
        """Buscar todos los usuarios de facturación incluyendo inactivos"""
        facturacion_list = await self.facturacion_repository.search_all_facturacion_including_inactive(search_params)
        return [self._to_response(facturacion) for facturacion in facturacion_list]
    
    async def get_facturacion_activos(self) -> List[FacturacionResponse]:
        """Obtener todos los usuarios de facturación activos"""
        facturacion_list = await self.facturacion_repository.get_activos()
        return [self._to_response(facturacion) for facturacion in facturacion_list]
    
    async def get_facturacion_inactivos(self) -> List[FacturacionResponse]:
        """Obtener todos los usuarios de facturación inactivos"""
        facturacion_list = await self.facturacion_repository.get_inactivos()
        return [self._to_response(facturacion) for facturacion in facturacion_list]
    
    async def get_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas de usuarios de facturación"""
        total_activos = await self.facturacion_repository.count_by_status(True)
        total_inactivos = await self.facturacion_repository.count_by_status(False)
        
        return {
            "total_activos": total_activos,
            "total_inactivos": total_inactivos,
            "total_general": total_activos + total_inactivos
        }
    
    def _to_response(self, facturacion: Facturacion) -> FacturacionResponse:
        """Convertir modelo a respuesta"""
        return FacturacionResponse(
            id=str(facturacion.id),
            facturacion_name=facturacion.facturacion_name,
            facturacion_code=facturacion.facturacion_code,
            facturacion_email=facturacion.facturacion_email,
            is_active=facturacion.is_active,
            observaciones=facturacion.observaciones or "",
            fecha_creacion=facturacion.fecha_creacion or datetime.now(timezone.utc),
            fecha_actualizacion=facturacion.fecha_actualizacion or datetime.now(timezone.utc)
        )
