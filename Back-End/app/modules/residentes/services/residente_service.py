from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.modules.residentes.repositories.residente_repository import ResidenteRepository
from app.modules.residentes.models.residente import Residente
from app.modules.residentes.schemas.residente import (
    ResidenteCreate,
    ResidenteUpdate,
    ResidenteResponse,
    ResidenteSearch
)
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ConflictError
)
from app.shared.services.user_management import UserManagementService

class ResidenteService:
    """Servicio para la lógica de negocio de Residentes"""
    
    def __init__(self, residente_repository: ResidenteRepository, user_management_service: UserManagementService):
        self.residente_repository = residente_repository
        self.user_management_service = user_management_service
    
    async def create_residente(self, residente_data: ResidenteCreate) -> ResidenteResponse:
        """Crear un nuevo residente y su usuario correspondiente"""
        # Verificar que el email no esté en uso en residentes
        existing_email = await self.residente_repository.get_by_email(residente_data.residente_email)
        if existing_email:
            raise ConflictError("El email ya está registrado en residentes")
        
        # Verificar que el email no esté en uso en usuarios
        email_exists_in_users = await self.user_management_service.check_email_exists_in_users(residente_data.residente_email)
        if email_exists_in_users:
            raise ConflictError("El email ya está registrado en usuarios")
        
        # Verificar que el código no esté en uso
        existing_codigo = await self.residente_repository.get_by_codigo(residente_data.residente_code)
        if existing_codigo:
            raise ConflictError("El código ya está registrado")
        
        # Verificar que el registro médico no esté en uso
        existing_registro = await self.residente_repository.get_by_registro_medico(residente_data.registro_medico)
        if existing_registro:
            raise ConflictError("El registro médico ya está registrado")
        
        # Extraer la contraseña para crear el usuario
        password = residente_data.password
        
        # Crear el residente y usuario
        residente = None
        user = None
        
        try:
            # Crear el residente en la colección residentes
            residente = await self.residente_repository.create_residente_from_schema(residente_data)
            
            # Crear el usuario en la colección usuarios con rol "residente"
            user = await self.user_management_service.create_user_for_resident(
                name=residente_data.residente_name,
                email=residente_data.residente_email,
                password=password,
                is_active=residente_data.is_active
            )
            
            return self._to_response(residente)
            
        except Exception as e:
            # Rollback: si se creó el residente pero falló la creación del usuario, eliminar el residente
            if residente and not user:
                try:
                    await self.residente_repository.delete(str(residente.id))
                except:
                    pass
            
            # Rollback: si se creó el usuario pero falló algo más, eliminar el usuario
            if user and not residente:
                try:
                    await self.user_management_service.delete_user_by_email(residente_data.ResidenteEmail)
                except:
                    pass
            
            # Re-lanzar la excepción original
            if "email ya está registrado" in str(e) or "Ya existe un usuario con el email" in str(e):
                raise ConflictError(str(e))
            else:
                raise BadRequestError(f"Error al crear residente: {str(e)}")
    
    async def get_residente(self, residente_code: str) -> ResidenteResponse:
        """Obtener un residente por código"""
        residente = await self.residente_repository.get_by_codigo(residente_code)
        if not residente:
            raise NotFoundError("Residente no encontrado")
        return self._to_response(residente)
    
    async def get_residentes(self, skip: int = 0, limit: int = 10) -> List[ResidenteResponse]:
        """Obtener lista de residentes activos con paginación"""
        residentes = await self.residente_repository.get_multi(
            filters={"is_active": True},
            skip=skip,
            limit=limit
        )
        return [self._to_response(residente) for residente in residentes]
    
    async def update_residente(self, residente_code: str, residente_data: ResidenteUpdate) -> ResidenteResponse:
        """Actualizar un residente"""
        # Verificar que el residente existe
        existing_residente = await self.residente_repository.get_by_codigo(residente_code)
        if not existing_residente:
            raise NotFoundError("Residente no encontrado")
        
        # Verificar unicidad del email si se está actualizando
        if residente_data.residente_email:
            existing_email = await self.residente_repository.get_by_email(residente_data.residente_email)
            if existing_email and str(existing_email.id) != str(existing_residente.id):
                raise ConflictError("El email ya está registrado por otro residente")
        
        # Verificar unicidad del código si se está actualizando
        if residente_data.residente_code:
            existing_codigo = await self.residente_repository.get_by_codigo(residente_data.residente_code)
            if existing_codigo and str(existing_codigo.id) != str(existing_residente.id):
                raise ConflictError("El código ya está registrado por otro residente")
        
        # Verificar unicidad del registro médico si se está actualizando
        if residente_data.registro_medico:
            existing_registro = await self.residente_repository.get_by_registro_medico(residente_data.registro_medico)
            if existing_registro and str(existing_registro.id) != str(existing_residente.id):
                raise ConflictError("El registro médico ya está registrado por otro residente")
        
        # Actualizar el residente y sincronizar con la colección usuarios
        try:
            updated_residente = await self.residente_repository.update(str(existing_residente.id), residente_data)
            if not updated_residente:
                raise BadRequestError("Error al actualizar el residente")

            # Sincronizar cambios con colección usuarios
            try:
                # Tomar valores definitivos del objeto actualizado (si lo tenemos) para evitar inconsistencias
                final_name = updated_residente.residente_name if hasattr(updated_residente, 'residente_name') else (residente_data.residente_name or existing_residente.residente_name)
                final_email = updated_residente.residente_email if hasattr(updated_residente, 'residente_email') else (residente_data.residente_email or existing_residente.residente_email)
                final_is_active = updated_residente.is_active if hasattr(updated_residente, 'is_active') else (
                    residente_data.is_active if residente_data.is_active is not None else existing_residente.is_active
                )
                await self.user_management_service.update_user_for_resident(
                    existing_residente.residente_email,
                    name=final_name,
                    new_email=final_email,
                    is_active=final_is_active,
                    new_password=(residente_data.password if hasattr(residente_data, 'password') else None)
                )
            except Exception as sync_error:
                # No romper la operación principal si falla la sincronización, pero registrar el error
                # Podríamos agregar un sistema de eventos para reintentar
                print(f"Warning: Falló sincronización con usuarios para residente {residente_code}: {sync_error}")

            return self._to_response(updated_residente)
        except Exception as e:
            raise BadRequestError(f"Error al actualizar el residente: {str(e)}")
    
    async def delete_residente(self, residente_code: str) -> bool:
        """Eliminar (soft delete) un residente"""
        residente = await self.residente_repository.get_by_codigo(residente_code)
        if not residente:
            raise NotFoundError("Residente no encontrado")
        
        try:
            return await self.residente_repository.delete(str(residente.id))
        except Exception as e:
            raise BadRequestError(f"Error al eliminar el residente: {str(e)}")
    
    async def toggle_estado(self, residente_code: str) -> ResidenteResponse:
        """Cambiar el estado activo/inactivo de un residente"""
        residente = await self.residente_repository.get_by_codigo(residente_code)
        if not residente:
            raise NotFoundError("Residente no encontrado")
        
        # Cambiar el estado del residente
        nuevo_estado = not residente.is_active
        
        # Crear objeto de actualización con todos los campos requeridos
        update_data = ResidenteUpdate(
            residente_name=residente.residente_name,
            residente_code=residente.residente_code,
            residente_email=residente.residente_email,
            registro_medico=residente.registro_medico,
            observaciones=residente.observaciones,
            is_active=nuevo_estado
        )
        
        try:
            updated_residente = await self.residente_repository.update(str(residente.id), update_data)
            if not updated_residente:
                raise BadRequestError("Error al cambiar el estado del residente")
            return self._to_response(updated_residente)
        except Exception as e:
            raise BadRequestError(f"Error al cambiar el estado del residente: {str(e)}")
    
    async def search_residentes(self, search_params: ResidenteSearch, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Búsqueda avanzada de residentes"""
        residentes = await self.residente_repository.search_residentes(search_params, skip, limit)
        total = await self.residente_repository.count_search_results(search_params)
        
        return {
            "residentes": [self._to_response(residente) for residente in residentes if residente],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def search_active_residentes(self, search_params: ResidenteSearch, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Búsqueda de solo residentes activos"""
        residentes = await self.residente_repository.search_active_residentes(search_params, skip, limit)
        total = await self.residente_repository.count_active_search_results(search_params)
        
        return {
            "residentes": [self._to_response(residente) for residente in residentes if residente],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def search_all_residentes_including_inactive(self, search_params: ResidenteSearch, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """Búsqueda de todos los residentes incluyendo inactivos"""
        residentes = await self.residente_repository.search_all_residentes_including_inactive(search_params, skip, limit)
        total = await self.residente_repository.count_all_search_results(search_params)
        
        return {
            "residentes": [self._to_response(residente) for residente in residentes if residente],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def _to_response(self, residente: Residente) -> ResidenteResponse:
        """Convertir modelo Residente a ResidenteResponse"""
        return ResidenteResponse(
            id=str(residente.id),
            residente_name=residente.residente_name,
            iniciales_residente=residente.iniciales_residente or "",
            residente_code=residente.residente_code,
            residente_email=residente.residente_email,
            registro_medico=residente.registro_medico,
            observaciones=residente.observaciones or "",
            is_active=residente.is_active,
            fecha_creacion=residente.fecha_creacion or datetime.now(timezone.utc),
            fecha_actualizacion=residente.fecha_actualizacion or datetime.now(timezone.utc)
        )