"""Servicio para la lógica de negocio de Pathologists"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.pathologists.schemas.pathologist import PathologistCreate, PathologistUpdate, PathologistResponse, PathologistSearch
from app.modules.pathologists.repositories.pathologist_repository import PathologistRepository
from app.shared.services.user_management import UserManagementService

class PathologistService:
    """Servicio para la lógica de negocio de Pathologists"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PathologistRepository(db)
        self.user_service = UserManagementService(db)
    
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
        
        # Crear el patólogo en la colección pathologists
        doc = await self.repo.create(payload)
        
        # Crear el usuario en la colección users
        user_data = await self.user_service.create_user_for_pathologist(
            name=payload.pathologist_name,
            email=payload.pathologist_email,
            password=payload.password,
            pathologist_code=payload.pathologist_code,
            is_active=payload.is_active
        )
        
        if not user_data:
            # Si falla la creación del usuario, eliminar el patólogo creado
            await self.repo.delete_by_pathologist_code(payload.pathologist_code)
            raise ConflictError("Failed to create user account")
        
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
        update_data = payload.model_dump(exclude_unset=True)
        updated = await self.repo.update_by_pathologist_code(pathologist_code, update_data)
        if not updated:
            raise BadRequestError("Failed to update pathologist")
        
        # Actualizar el usuario correspondiente en la colección users
        if payload.pathologist_name or payload.pathologist_email or payload.is_active is not None or payload.password:
            user_data = await self.user_service.update_user_for_pathologist(
                pathologist_code=pathologist_code,
                name=payload.pathologist_name,
                email=payload.pathologist_email,
                password=payload.password,
                is_active=payload.is_active
            )
            if not user_data:
                # Si falla la actualización del usuario, revertir cambios en pathologist
                # (opcional: implementar rollback si es crítico)
                pass
        
        return self._to_response(updated)
    
    async def delete_pathologist(self, pathologist_code: str) -> Dict[str, Any]:
        """Eliminar patólogo por código"""
        doc = await self.repo.get_by_pathologist_code(pathologist_code)
        if not doc:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        ok = await self.repo.delete_by_pathologist_code(pathologist_code)
        return {"deleted": ok, "pathologist_code": pathologist_code}
    
    async def update_signature(self, pathologist_code: str, signature_url: str) -> PathologistResponse:
        """Actualizar solo la firma digital de un patólogo"""
        # Verificar que el patólogo existe
        existing = await self.repo.get_by_pathologist_code(pathologist_code)
        if not existing:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        # Actualizar solo la firma
        updated = await self.repo.update_signature_by_code(pathologist_code, signature_url)
        if not updated:
            raise BadRequestError("Failed to update signature")
        
        return self._to_response(updated)

    async def get_signature(self, pathologist_code: str) -> Dict[str, str]:
        """Obtener solo la firma digital de un patólogo"""
        doc = await self.repo.get_by_pathologist_code(pathologist_code)
        if not doc:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        return {
            "pathologist_code": pathologist_code,
            "signature": doc.get("signature", "")
        }

    async def upload_signature_file(self, pathologist_code: str, file_content: bytes, filename: str) -> PathologistResponse:
        """Subir archivo de firma y actualizar la URL en la base de datos"""
        import os
        import uuid
        from datetime import datetime, timezone
        
        # Verificar que el patólogo existe
        existing = await self.repo.get_by_pathologist_code(pathologist_code)
        if not existing:
            raise NotFoundError(f"Pathologist with code {pathologist_code} not found")
        
        # Validar tipo de archivo
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.svg']
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise BadRequestError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        # Validar tamaño (1MB máximo)
        max_size = 1024 * 1024  # 1MB
        if len(file_content) > max_size:
            raise BadRequestError("File size too large. Maximum size is 1MB")
        
        # Crear directorio de firmas si no existe
        signatures_dir = "uploads/signatures"
        os.makedirs(signatures_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        unique_filename = f"{pathologist_code}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(signatures_dir, unique_filename)
        
        # Guardar archivo
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise BadRequestError(f"Failed to save file: {str(e)}")
        
        # Generar URL relativa
        signature_url = f"/uploads/signatures/{unique_filename}"
        
        # Actualizar en base de datos
        updated = await self.repo.update_signature_by_code(pathologist_code, signature_url)
        if not updated:
            # Si falla la actualización, eliminar el archivo
            try:
                os.remove(file_path)
            except:
                pass
            raise BadRequestError("Failed to update signature in database")
        
        return self._to_response(updated)

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