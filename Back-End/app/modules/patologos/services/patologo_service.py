"""Servicio para la lógica de negocio de Patólogos"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.modules.patologos.models.patologo import Patologo
from app.modules.patologos.schemas.patologo import (
    PatologoCreate,
    PatologoUpdate,
    PatologoResponse,
    PatologoSearch
)
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    ConflictError
)
from app.shared.services.user_management import UserManagementService

class PatologoService:
    """Servicio para la lógica de negocio de Patólogos"""
    
    def __init__(self, patologo_repository: PatologoRepository, user_management_service: UserManagementService):
        self.patologo_repository = patologo_repository
        self.user_management_service = user_management_service
    
    async def create_patologo(self, patologo_data: PatologoCreate) -> PatologoResponse:
        """Crear un nuevo patólogo y su usuario correspondiente"""
        # Verificar que el email no esté en uso en patólogos
        existing_email = await self.patologo_repository.get_by_email(patologo_data.PatologoEmail)
        if existing_email:
            raise ConflictError("El email ya está registrado en patólogos")
        
        # Verificar que el email no esté en uso en usuarios
        email_exists_in_users = await self.user_management_service.check_email_exists_in_users(patologo_data.PatologoEmail)
        if email_exists_in_users:
            raise ConflictError("El email ya está registrado en usuarios")
        
        # Verificar que el código no esté en uso
        existing_codigo = await self.patologo_repository.get_by_codigo(patologo_data.patologoCode)
        if existing_codigo:
            raise ConflictError("El código ya está registrado")
        
        # Verificar que el registro médico no esté en uso
        existing_registro = await self.patologo_repository.get_by_registro_medico(patologo_data.registro_medico)
        if existing_registro:
            raise ConflictError("El registro médico ya está registrado")
        
        # Extraer la contraseña y crear datos del patólogo sin ella
        password = patologo_data.password
        
        # Crear el patólogo y usuario
        patologo = None
        user = None
        
        try:
            # Crear el patólogo en la colección patólogos
            patologo = await self.patologo_repository.create_patologo_from_schema(patologo_data)
            
            # Crear el usuario en la colección usuarios
            user = await self.user_management_service.create_user_for_pathologist(
                name=patologo_data.patologoName,
                email=patologo_data.PatologoEmail,
                password=password,
                is_active=patologo_data.isActive
            )
            
            return self._to_response(patologo)
            
        except Exception as e:
            # Rollback: si se creó el patólogo pero falló la creación del usuario, eliminar el patólogo
            if patologo and not user:
                try:
                    await self.patologo_repository.delete(str(patologo.id))
                except:
                    pass
            
            # Rollback: si se creó el usuario pero falló algo más, eliminar el usuario
            if user and not patologo:
                try:
                    await self.user_management_service.delete_user_by_email(patologo_data.PatologoEmail)
                except:
                    pass
            
            # Re-lanzar la excepción original
            if "email ya está registrado" in str(e) or "Ya existe un usuario con el email" in str(e):
                raise ConflictError(str(e))
            else:
                raise BadRequestError(f"Error al crear patólogo: {str(e)}")
    

    
    async def get_patologo(self, patologo_code: str) -> PatologoResponse:
        """Obtener un patólogo por código"""
        patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        return self._to_response(patologo)
    
    async def get_patologos(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PatologoResponse]:
        """Obtener lista de patólogos activos"""
        filters = {"isActive": True}
        patologos = await self.patologo_repository.get_multi(skip=skip, limit=limit, filters=filters)
        return [self._to_response(patologo) for patologo in patologos]
    

    
    async def update_patologo(self, patologo_code: str, patologo_data: PatologoUpdate) -> PatologoResponse:
        """Actualizar un patólogo por código"""
        # Verificar que el patólogo existe
        existing_patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not existing_patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Verificar unicidad de email si se está actualizando
        if patologo_data.PatologoEmail and patologo_data.PatologoEmail != existing_patologo.PatologoEmail:
            existing_email = await self.patologo_repository.get_by_email(patologo_data.PatologoEmail)
            if existing_email and str(existing_email.id) != str(existing_patologo.id):
                raise ConflictError("El email ya está registrado")
        
        # Verificar unicidad de código si se está actualizando
        if patologo_data.patologoCode and patologo_data.patologoCode != existing_patologo.patologoCode:
            existing_codigo = await self.patologo_repository.get_by_codigo(patologo_data.patologoCode)
            if existing_codigo and str(existing_codigo.id) != str(existing_patologo.id):
                raise ConflictError("El código ya está registrado")
        
        # Quitar "firma" del update si llega (no se debe actualizar)
        if hasattr(patologo_data, 'firma'):
            try:
                setattr(patologo_data, 'firma', None)
            except Exception:
                pass

        # Actualizar el patólogo usando su ID interno
        updated_patologo = await self.patologo_repository.update(str(existing_patologo.id), patologo_data)
        if not updated_patologo:
            raise NotFoundError("Error al actualizar el patólogo")

        # Sincronizar cambios con colección usuarios (nombre, email, estado, password opcional)
        try:
            final_name = getattr(updated_patologo, 'patologoName', existing_patologo.patologoName)
            final_email = getattr(updated_patologo, 'PatologoEmail', existing_patologo.PatologoEmail)
            final_is_active = getattr(updated_patologo, 'isActive', existing_patologo.isActive)
            await self.user_management_service.update_user_for_resident(
                old_email=existing_patologo.PatologoEmail,
                name=final_name,
                new_email=final_email,
                is_active=final_is_active,
                new_password=(patologo_data.password if hasattr(patologo_data, 'password') else None)
            )
        except Exception as sync_err:
            print(f"Warning: Falló sincronización con usuarios para patólogo {patologo_code}: {sync_err}")

        return self._to_response(updated_patologo)
    
    async def toggle_patologo_status(self, patologo_code: str) -> PatologoResponse:
        """Cambiar el estado activo/inactivo de un patólogo por código"""
        patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Cambiar el estado del patólogo
        nuevo_estado = not patologo.isActive
        
        # Crear objeto de actualización con todos los campos requeridos
        patologo_update = PatologoUpdate(
            patologoName=patologo.patologoName,
            patologoCode=patologo.patologoCode,
            PatologoEmail=patologo.PatologoEmail,
            registro_medico=patologo.registro_medico,
            firma=patologo.firma,
            observaciones=patologo.observaciones,
            isActive=nuevo_estado
        )
        
        # Actualizar usando ID interno
        updated_patologo = await self.patologo_repository.update(str(patologo.id), patologo_update)
        if not updated_patologo:
            raise BadRequestError("Error al cambiar estado")
        
        return self._to_response(updated_patologo)
    

    
    async def delete_patologo(self, patologo_code: str) -> bool:
        """Eliminar un patólogo por código (eliminación permanente)"""
        patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Realizar eliminación permanente de la base de datos
        result = await self.patologo_repository.delete(str(patologo.id))
        return result
    
    async def search_patologos(
        self, 
        search_params: PatologoSearch, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[PatologoResponse]:
        """Búsqueda avanzada de patólogos"""
        patologos = await self.patologo_repository.search(search_params, skip=skip, limit=limit)
        return [self._to_response(patologo) for patologo in patologos]
    

    

    

    

    
    async def toggle_estado(self, patologo_code: str, nuevo_estado: bool) -> PatologoResponse:
        """Cambiar el estado activo/inactivo de un patólogo por código"""
        patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Cambiar estado usando ID interno
        update_data = PatologoUpdate(isActive=nuevo_estado)
        updated_patologo = await self.patologo_repository.update(str(patologo.id), update_data)
        if not updated_patologo:
            raise BadRequestError("Error al cambiar estado")
        
        return self._to_response(updated_patologo)
    
    async def update_firma(self, patologo_code: str, firma_url: str) -> PatologoResponse:
        """Actualizar la firma digital de un patólogo"""
        patologo = await self.patologo_repository.get_by_codigo(patologo_code)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Actualizar solo el campo firma
        patologo.firma = firma_url
        patologo.fecha_actualizacion = datetime.utcnow()
        
        # Guardar en la base de datos
        updated_patologo = await self.patologo_repository.update(str(patologo.id), patologo)
        if not updated_patologo:
            raise BadRequestError("Error al actualizar la firma")
        
        return self._to_response(updated_patologo)
    

    

    

    
    def _to_response(self, patologo: Patologo) -> PatologoResponse:
        """Convertir modelo a esquema de respuesta"""
        return PatologoResponse(
            id=str(patologo.id),
            patologoName=patologo.patologoName,
            InicialesPatologo=getattr(patologo, 'InicialesPatologo', None),
            patologoCode=patologo.patologoCode,
            PatologoEmail=patologo.PatologoEmail,
            registro_medico=patologo.registro_medico,
            isActive=patologo.isActive,
            firma=patologo.firma,
            observaciones=patologo.observaciones,
            fecha_creacion=patologo.fecha_creacion or datetime.utcnow(),
            fecha_actualizacion=patologo.fecha_actualizacion or datetime.utcnow()
        )