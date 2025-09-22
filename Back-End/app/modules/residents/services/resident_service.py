"""Servicio para la lógica de negocio de Residents"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.residents.schemas.resident import ResidentCreate, ResidentUpdate, ResidentResponse, ResidentSearch
from app.modules.residents.repositories.resident_repository import ResidentRepository
from app.shared.services.user_management import UserManagementService

class ResidentService:
    """Servicio para la lógica de negocio de Residents"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = ResidentRepository(db)
        self.user_service = UserManagementService(db)
    
    async def create_resident(self, payload: ResidentCreate) -> ResidentResponse:
        """Crear un nuevo residente"""
        # Verificar que el código no esté en uso
        existing_code = await self.repo.get_by_resident_code(payload.resident_code)
        if existing_code:
            raise ConflictError("Resident code already exists")
        
        # Verificar que el email no esté en uso
        existing_email = await self.repo.get_by_email(payload.resident_email)
        if existing_email:
            raise ConflictError("Email already exists")
        
        # Verificar que la licencia médica no esté en uso
        existing_license = await self.repo.get_by_medical_license(payload.medical_license)
        if existing_license:
            raise ConflictError("Medical license already exists")
        
        # Crear el residente en la colección residents
        doc = await self.repo.create(payload)
        
        # Crear el usuario en la colección users
        user_data = await self.user_service.create_user_for_resident(
            name=payload.resident_name,
            email=payload.resident_email,
            password=payload.password,
            resident_code=payload.resident_code,
            is_active=payload.is_active
        )
        
        if not user_data:
            # Si falla la creación del usuario, eliminar el residente creado
            await self.repo.delete_by_resident_code(payload.resident_code)
            raise ConflictError("Failed to create user account")
        
        return self._to_response(doc)
    
    async def get_resident(self, resident_code: str) -> ResidentResponse:
        """Obtener residente por código"""
        doc = await self.repo.get_by_resident_code(resident_code)
        if not doc:
            raise NotFoundError(f"Resident with code {resident_code} not found")
        return self._to_response(doc)
    
    async def list_residents(self, skip: int = 0, limit: int = 100) -> List[ResidentResponse]:
        """Listar residentes activos"""
        residents = await self.repo.list_active(skip=skip, limit=limit)
        return [self._to_response(resident) for resident in residents]
    
    async def search_residents(self, search_params: ResidentSearch, skip: int = 0, limit: int = 100) -> List[ResidentResponse]:
        """Buscar residentes"""
        residents = await self.repo.search(search_params, skip=skip, limit=limit)
        return [self._to_response(resident) for resident in residents]
    
    async def update_resident(self, resident_code: str, payload: ResidentUpdate) -> ResidentResponse:
        """Actualizar residente por código"""
        # Verificar que el residente existe
        existing = await self.repo.get_by_resident_code(resident_code)
        if not existing:
            raise NotFoundError(f"Resident with code {resident_code} not found")
        
        # Verificar unicidad de email si se está actualizando
        if payload.resident_email and payload.resident_email != existing["resident_email"]:
            existing_email = await self.repo.get_by_email(payload.resident_email)
            if existing_email:
                raise ConflictError("Email already exists")
        
        # Verificar unicidad de licencia médica si se está actualizando
        if payload.medical_license and payload.medical_license != existing["medical_license"]:
            existing_license = await self.repo.get_by_medical_license(payload.medical_license)
            if existing_license:
                raise ConflictError("Medical license already exists")
        
        # Actualizar el residente
        update_data = payload.dict(exclude_unset=True)
        updated = await self.repo.update_by_resident_code(resident_code, update_data)
        if not updated:
            raise BadRequestError("Failed to update resident")
        
        # Actualizar el usuario correspondiente en la colección users
        if payload.resident_name or payload.resident_email or payload.is_active is not None or payload.password:
            user_data = await self.user_service.update_user_for_resident(
                resident_code=resident_code,
                name=payload.resident_name,
                email=payload.resident_email,
                password=payload.password,
                is_active=payload.is_active
            )
            if not user_data:
                # Si falla la actualización del usuario, revertir cambios en resident
                # (opcional: implementar rollback si es crítico)
                pass
        
        return self._to_response(updated)
    
    async def delete_resident(self, resident_code: str) -> Dict[str, Any]:
        """Eliminar residente por código"""
        doc = await self.repo.get_by_resident_code(resident_code)
        if not doc:
            raise NotFoundError(f"Resident with code {resident_code} not found")
        
        ok = await self.repo.delete_by_resident_code(resident_code)
        return {"deleted": ok, "resident_code": resident_code}
    
    def _to_response(self, doc: dict) -> ResidentResponse:
        """Convertir documento a respuesta"""
        return ResidentResponse(
            id=doc["id"],
            resident_code=doc["resident_code"],
            resident_name=doc["resident_name"],
            initials=doc.get("initials"),
            resident_email=doc["resident_email"],
            medical_license=doc["medical_license"],
            is_active=doc["is_active"],
            observations=doc.get("observations"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
