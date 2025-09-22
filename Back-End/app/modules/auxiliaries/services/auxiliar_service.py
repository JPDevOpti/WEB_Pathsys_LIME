"""Servicio para la lógica de negocio de Auxiliaries"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.auxiliaries.schemas.auxiliar import AuxiliarCreate, AuxiliarUpdate, AuxiliarResponse, AuxiliarSearch
from app.modules.auxiliaries.repositories.auxiliar_repository import AuxiliarRepository
from app.shared.services.user_management import UserManagementService

class AuxiliarService:
    """Servicio para la lógica de negocio de Auxiliaries"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AuxiliarRepository(db)
        self.user_service = UserManagementService(db)
    
    async def create_auxiliar(self, payload: AuxiliarCreate) -> AuxiliarResponse:
        """Crear un nuevo auxiliar"""
        # Verificar que el código no esté en uso
        existing_code = await self.repo.get_by_auxiliar_code(payload.auxiliar_code)
        if existing_code:
            raise ConflictError("Auxiliar code already exists")
        
        # Verificar que el email no esté en uso
        existing_email = await self.repo.get_by_email(payload.auxiliar_email)
        if existing_email:
            raise ConflictError("Email already exists")
        
        # Crear el auxiliar en la colección auxiliaries
        doc = await self.repo.create(payload)
        
        # Crear el usuario en la colección users
        user_data = await self.user_service.create_user_for_auxiliar(
            name=payload.auxiliar_name,
            email=payload.auxiliar_email,
            password=payload.password,
            auxiliar_code=payload.auxiliar_code,
            is_active=payload.is_active
        )
        
        if not user_data:
            # Si falla la creación del usuario, eliminar el auxiliar creado
            await self.repo.delete_by_auxiliar_code(payload.auxiliar_code)
            raise ConflictError("Failed to create user account")
        
        return self._to_response(doc)
    
    async def get_auxiliar(self, auxiliar_code: str) -> AuxiliarResponse:
        """Obtener auxiliar por código"""
        doc = await self.repo.get_by_auxiliar_code(auxiliar_code)
        if not doc:
            raise NotFoundError(f"Auxiliar with code {auxiliar_code} not found")
        return self._to_response(doc)
    
    async def list_auxiliaries(self, skip: int = 0, limit: int = 100) -> List[AuxiliarResponse]:
        """Listar auxiliares activos"""
        auxiliaries = await self.repo.list_active(skip=skip, limit=limit)
        return [self._to_response(auxiliar) for auxiliar in auxiliaries]
    
    async def search_auxiliaries(self, search_params: AuxiliarSearch, skip: int = 0, limit: int = 100) -> List[AuxiliarResponse]:
        """Buscar auxiliares"""
        auxiliaries = await self.repo.search(search_params, skip=skip, limit=limit)
        return [self._to_response(auxiliar) for auxiliar in auxiliaries]
    
    async def update_auxiliar(self, auxiliar_code: str, payload: AuxiliarUpdate) -> AuxiliarResponse:
        """Actualizar auxiliar por código"""
        # Verificar que el auxiliar existe
        existing = await self.repo.get_by_auxiliar_code(auxiliar_code)
        if not existing:
            raise NotFoundError(f"Auxiliar with code {auxiliar_code} not found")
        
        # Verificar unicidad de email si se está actualizando
        if payload.auxiliar_email and payload.auxiliar_email != existing["auxiliar_email"]:
            existing_email = await self.repo.get_by_email(payload.auxiliar_email)
            if existing_email:
                raise ConflictError("Email already exists")
        
        # Actualizar el auxiliar
        update_data = payload.dict(exclude_unset=True)
        updated = await self.repo.update_by_auxiliar_code(auxiliar_code, update_data)
        if not updated:
            raise BadRequestError("Failed to update auxiliar")
        
        # Actualizar el usuario correspondiente en la colección users
        if payload.auxiliar_name or payload.auxiliar_email or payload.is_active is not None or payload.password:
            user_data = await self.user_service.update_user_for_auxiliar(
                auxiliar_code=auxiliar_code,
                name=payload.auxiliar_name,
                email=payload.auxiliar_email,
                password=payload.password,
                is_active=payload.is_active
            )
            if not user_data:
                # Si falla la actualización del usuario, revertir cambios en auxiliar
                # (opcional: implementar rollback si es crítico)
                pass
        
        return self._to_response(updated)
    
    async def delete_auxiliar(self, auxiliar_code: str) -> Dict[str, Any]:
        """Eliminar auxiliar por código"""
        doc = await self.repo.get_by_auxiliar_code(auxiliar_code)
        if not doc:
            raise NotFoundError(f"Auxiliar with code {auxiliar_code} not found")
        
        ok = await self.repo.delete_by_auxiliar_code(auxiliar_code)
        return {"deleted": ok, "auxiliar_code": auxiliar_code}
    
    def _to_response(self, doc: dict) -> AuxiliarResponse:
        """Convertir documento a respuesta"""
        return AuxiliarResponse(
            id=doc["id"],
            auxiliar_code=doc["auxiliar_code"],
            auxiliar_name=doc["auxiliar_name"],
            auxiliar_email=doc["auxiliar_email"],
            is_active=doc["is_active"],
            observations=doc.get("observations"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
