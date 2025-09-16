"""Servicio para la lógica de negocio de Pathologists"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.pathologists.schemas.pathologist import PathologistCreate, PathologistUpdate, PathologistResponse, PathologistSearch
from app.modules.pathologists.repositories.pathologist_repository import PathologistRepository

class PathologistService:
    """Servicio para la lógica de negocio de Pathologists"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PathologistRepository(db)
    
    async def create_pathologist(self, payload: PathologistCreate) -> PathologistResponse:
        """Crear un nuevo patólogo"""
        # Verificar que el código no esté en uso
        existing_code = await self.repo.get_by_pathologist_code(payload.pathologist_code)
        if existing_code:
            raise ConflictError("Pathologist code already exists")
        
        # Verificar que el email no esté en uso
        existing_email = await self.repo.get_by_email(payload.pathologist_email)
        if existing_email:
            raise ConflictError("Email already exists")
        
        # Verificar que la licencia médica no esté en uso
        existing_license = await self.repo.get_by_medical_license(payload.medical_license)
        if existing_license:
            raise ConflictError("Medical license already exists")
        
        # Crear el patólogo
        doc = await self.repo.create(payload)
        return self._to_response(doc)
    
    async def get_pathologist(self, pathologist_code: str) -> PathologistResponse:
        """Obtener patólogo por código"""
        doc = await self.repo.get_by_pathologist_code(pathologist_code)
        if not doc:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        return self._to_response(doc)
    
    async def list_pathologists(self, skip: int = 0, limit: int = 100) -> List[PathologistResponse]:
        """Listar patólogos activos"""
        pathologists = await self.repo.list_active(skip=skip, limit=limit)
        return [self._to_response(pathologist) for pathologist in pathologists]
    
    async def search_pathologists(self, search_params: PathologistSearch, skip: int = 0, limit: int = 100) -> List[PathologistResponse]:
        """Buscar patólogos"""
        pathologists = await self.repo.search(search_params, skip=skip, limit=limit)
        return [self._to_response(pathologist) for pathologist in pathologists]
    
    async def update_pathologist(self, pathologist_code: str, payload: PathologistUpdate) -> PathologistResponse:
        """Actualizar patólogo por código"""
        # Verificar que el patólogo existe
        existing = await self.repo.get_by_pathologist_code(pathologist_code)
        if not existing:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        # Verificar unicidad de email si se está actualizando
        if payload.pathologist_email and payload.pathologist_email != existing["pathologist_email"]:
            existing_email = await self.repo.get_by_email(payload.pathologist_email)
            if existing_email:
                raise ConflictError("Email already exists")
        
        # Verificar unicidad de licencia médica si se está actualizando
        if payload.medical_license and payload.medical_license != existing["medical_license"]:
            existing_license = await self.repo.get_by_medical_license(payload.medical_license)
            if existing_license:
                raise ConflictError("Medical license already exists")
        
        # Actualizar el patólogo
        update_data = payload.dict(exclude_unset=True)
        updated = await self.repo.update_by_pathologist_code(pathologist_code, update_data)
        if not updated:
            raise BadRequestError("Failed to update pathologist")
        
        return self._to_response(updated)
    
    async def delete_pathologist(self, pathologist_code: str) -> Dict[str, Any]:
        """Eliminar patólogo por código"""
        doc = await self.repo.get_by_pathologist_code(pathologist_code)
        if not doc:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        ok = await self.repo.delete_by_pathologist_code(pathologist_code)
        return {"deleted": ok, "pathologist_code": pathologist_code}
    
    def _to_response(self, doc: Dict[str, Any]) -> PathologistResponse:
        """Convertir documento a respuesta"""
        from datetime import datetime, timezone
        
        # Asegurar que los campos de timestamp estén presentes
        created_at = doc.get("created_at")
        if created_at is None:
            created_at = datetime.now(timezone.utc)
        
        updated_at = doc.get("updated_at")
        if updated_at is None:
            updated_at = datetime.now(timezone.utc)
        
        return PathologistResponse(
            id=doc["id"],
            pathologist_code=doc["pathologist_code"],
            pathologist_name=doc["pathologist_name"],
            initials=doc.get("initials"),
            pathologist_email=doc["pathologist_email"],
            medical_license=doc["medical_license"],
            is_active=doc["is_active"],
            signature=doc.get("signature", ""),
            observations=doc.get("observations"),
            created_at=created_at,
            updated_at=updated_at
        )