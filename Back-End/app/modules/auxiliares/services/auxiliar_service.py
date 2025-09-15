import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId

from app.modules.auxiliares.repositories.auxiliar_repository import AuxiliarRepository
from app.modules.auxiliares.models.auxiliar import Auxiliar
from app.modules.auxiliares.schemas.auxiliar import (
    AuxiliarCreate,
    AuxiliarUpdate,
    AuxiliarResponse,
    AuxiliarSearch
)
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ConflictError
)
from app.shared.services.user_management import UserManagementService

logger = logging.getLogger(__name__)

class AuxiliarService:
    """Servicio para la lógica de negocio de Auxiliares"""
    
    def __init__(self, auxiliar_repository: AuxiliarRepository, user_management_service: UserManagementService):
        self.auxiliar_repository = auxiliar_repository
        self.user_management_service = user_management_service
    
    async def create_auxiliar(self, auxiliar_data: AuxiliarCreate) -> AuxiliarResponse:
        """Crear un nuevo auxiliar y su usuario correspondiente"""
        # Verificar que el email no esté en uso en auxiliares
        existing_email = await self.auxiliar_repository.get_by_email(auxiliar_data.auxiliar_email)
        if existing_email:
            raise ConflictError("El email ya está registrado en auxiliares")
        
        # Verificar que el email no esté en uso en usuarios
        email_exists_in_users = await self.user_management_service.check_email_exists_in_users(auxiliar_data.auxiliar_email)
        if email_exists_in_users:
            raise ConflictError("El email ya está registrado en usuarios")
        
        # Verificar que el código no esté en uso
        existing_codigo = await self.auxiliar_repository.get_by_codigo(auxiliar_data.auxiliar_code)
        if existing_codigo:
            raise ConflictError("El código ya está registrado")
        
        # Extraer la contraseña para crear el usuario
        password = auxiliar_data.password
        
        # Crear el auxiliar y usuario
        auxiliar = None
        user = None
        
        try:
            # Crear el auxiliar en la colección auxiliares
            auxiliar = await self.auxiliar_repository.create_auxiliar_from_schema(auxiliar_data)
            
            # Crear el usuario en la colección usuarios con rol "auxiliar"
            user = await self.user_management_service.create_user_for_auxiliary(
                name=auxiliar_data.auxiliar_name,
                email=auxiliar_data.auxiliar_email,
                password=password,
                is_active=auxiliar_data.is_active,
                auxiliar_code=auxiliar_data.auxiliar_code
            )
            
            return self._to_response(auxiliar)
            
        except Exception as e:
            # Rollback: si se creó el auxiliar pero falló la creación del usuario, eliminar el auxiliar
            if auxiliar and not user:
                try:
                    await self.auxiliar_repository.delete(str(auxiliar.id))
                except:
                    pass
            
            # Rollback: si se creó el usuario pero falló algo más, eliminar el usuario
            if user and not auxiliar:
                try:
                    await self.user_management_service.delete_user_by_email(auxiliar_data.auxiliar_email)
                except:
                    pass
            
            # Re-lanzar la excepción original
            if "email ya está registrado" in str(e) or "Ya existe un usuario con el email" in str(e):
                raise ConflictError(str(e))
            else:
                raise BadRequestError(f"Error al crear auxiliar: {str(e)}")
    
    async def get_auxiliar(self, auxiliar_code: str) -> AuxiliarResponse:
        """Obtener un auxiliar por código"""
        auxiliar = await self.auxiliar_repository.get_by_codigo(auxiliar_code)
        if not auxiliar:
            raise NotFoundError("Auxiliar no encontrado")
        return self._to_response(auxiliar)
    
    async def get_auxiliares(self, skip: int = 0, limit: int = 10) -> List[AuxiliarResponse]:
        """Obtener lista de auxiliares activos con paginación"""
        auxiliares = await self.auxiliar_repository.get_multi(
            filters={"is_active": True},
            skip=skip,
            limit=limit
        )
        return [self._to_response(auxiliar) for auxiliar in auxiliares]
    
    async def update_auxiliar(self, auxiliar_code: str, auxiliar_data: AuxiliarUpdate) -> AuxiliarResponse:
        """Actualizar un auxiliar"""
        # Verificar que el auxiliar existe
        existing_auxiliar = await self.auxiliar_repository.get_by_codigo(auxiliar_code)
        if not existing_auxiliar:
            raise NotFoundError("Auxiliar no encontrado")
        
        # Verificar conflictos de email si se está actualizando
        if auxiliar_data.auxiliar_email and auxiliar_data.auxiliar_email != existing_auxiliar.auxiliar_email:
            email_exists = await self.auxiliar_repository.exists_by_email(
                auxiliar_data.auxiliar_email, 
                exclude_id=ObjectId(existing_auxiliar.id)
            )
            if email_exists:
                raise ConflictError("El email ya está registrado")
        
        # Verificar conflictos de código si se está actualizando
        if auxiliar_data.auxiliar_code and auxiliar_data.auxiliar_code != existing_auxiliar.auxiliar_code:
            codigo_exists = await self.auxiliar_repository.exists_by_codigo(
                auxiliar_data.auxiliar_code,
                exclude_id=ObjectId(existing_auxiliar.id)
            )
            if codigo_exists:
                raise ConflictError("El código ya está registrado")
        
        # Actualizar el auxiliar y sincronizar con la colección usuarios
        try:
            updated_auxiliar = await self.auxiliar_repository.update(str(existing_auxiliar.id), auxiliar_data)
            if updated_auxiliar is None:
                raise NotFoundError(f"No se pudo actualizar el auxiliar con código {auxiliar_code}")

            # Sincronizar cambios con la colección usuarios (similar a residentes)
            try:
                final_name = getattr(updated_auxiliar, 'auxiliar_name', None) or auxiliar_data.auxiliar_name or existing_auxiliar.auxiliar_name
                final_email = getattr(updated_auxiliar, 'auxiliar_email', None) or auxiliar_data.auxiliar_email or existing_auxiliar.auxiliar_email
                final_is_active = getattr(updated_auxiliar, 'is_active', None)
                if final_is_active is None:
                    final_is_active = auxiliar_data.is_active if auxiliar_data.is_active is not None else existing_auxiliar.is_active

                await self.user_management_service.update_user_for_auxiliary(
                    existing_auxiliar.auxiliar_email,
                    name=final_name,
                    new_email=final_email,
                    is_active=final_is_active,
                    new_password=(auxiliar_data.password if hasattr(auxiliar_data, 'password') else None)
                )
            except Exception as sync_error:
                logger.warning(f"Falló sincronización con usuarios para auxiliar {auxiliar_code}: {sync_error}")

            return self._to_response(updated_auxiliar)
        except Exception as e:
            raise BadRequestError(f"Error al actualizar el auxiliar: {str(e)}")
    
    async def delete_auxiliar(self, auxiliar_code: str) -> bool:
        """Eliminar permanentemente un auxiliar"""
        auxiliar = await self.auxiliar_repository.get_by_codigo(auxiliar_code)
        if not auxiliar:
            raise NotFoundError("Auxiliar no encontrado")
        
        return await self.auxiliar_repository.hard_delete_by_codigo(auxiliar_code)
    
    async def activate_auxiliar(self, auxiliar_code: str) -> AuxiliarResponse:
        """Activar un auxiliar"""
        auxiliar = await self.auxiliar_repository.get_by_codigo(auxiliar_code)
        if not auxiliar:
            raise NotFoundError("Auxiliar no encontrado")
        
        if auxiliar.is_active:
            raise BadRequestError("El auxiliar ya está activo")
        
        success = await self.auxiliar_repository.activate_by_codigo(auxiliar_code)
        if not success:
            raise BadRequestError("No se pudo activar el auxiliar")
        
        # Obtener el auxiliar actualizado
        updated_auxiliar = await self.auxiliar_repository.get_by_codigo(auxiliar_code)
        if updated_auxiliar is None:
            raise NotFoundError(f"No se pudo obtener el auxiliar activado con código {auxiliar_code}")
        return self._to_response(updated_auxiliar)
    
    async def search_auxiliares(self, search_params: AuxiliarSearch) -> List[AuxiliarResponse]:
        """Buscar auxiliares con filtros"""
        auxiliares = await self.auxiliar_repository.search_auxiliares(search_params)
        return [self._to_response(auxiliar) for auxiliar in auxiliares]

    async def search_active_auxiliares(self, search_params: AuxiliarSearch) -> List[AuxiliarResponse]:
        """Buscar solo auxiliares activos con filtros"""
        auxiliares = await self.auxiliar_repository.search_active_auxiliares(search_params)
        return [self._to_response(auxiliar) for auxiliar in auxiliares]

    async def search_all_auxiliares_including_inactive(self, search_params: AuxiliarSearch) -> List[AuxiliarResponse]:
        """Buscar todos los auxiliares incluyendo inactivos"""
        auxiliares = await self.auxiliar_repository.search_all_auxiliares_including_inactive(search_params)
        return [self._to_response(auxiliar) for auxiliar in auxiliares]
    
    async def get_auxiliares_activos(self) -> List[AuxiliarResponse]:
        """Obtener todos los auxiliares activos"""
        auxiliares = await self.auxiliar_repository.get_activos()
        return [self._to_response(auxiliar) for auxiliar in auxiliares]
    
    async def get_auxiliares_inactivos(self) -> List[AuxiliarResponse]:
        """Obtener todos los auxiliares inactivos"""
        auxiliares = await self.auxiliar_repository.get_inactivos()
        return [self._to_response(auxiliar) for auxiliar in auxiliares]
    
    async def get_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas de auxiliares"""
        total_activos = await self.auxiliar_repository.count_by_status(True)
        total_inactivos = await self.auxiliar_repository.count_by_status(False)
        
        return {
            "total_activos": total_activos,
            "total_inactivos": total_inactivos,
            "total_general": total_activos + total_inactivos
        }
    
    def _to_response(self, auxiliar: Auxiliar) -> AuxiliarResponse:
        """Convertir modelo a respuesta"""
        return AuxiliarResponse(
            id=str(auxiliar.id),
            auxiliar_name=auxiliar.auxiliar_name,
            auxiliar_code=auxiliar.auxiliar_code,
            auxiliar_email=auxiliar.auxiliar_email,
            is_active=auxiliar.is_active,
            observaciones=auxiliar.observaciones or "",
            fecha_creacion=auxiliar.fecha_creacion or datetime.now(timezone.utc),
            fecha_actualizacion=auxiliar.fecha_actualizacion or datetime.now(timezone.utc)
        )