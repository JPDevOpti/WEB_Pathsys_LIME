"""Repositorio para operaciones CRUD de Pathologists"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from ..schemas import PathologistCreate, PathologistUpdate, PathologistSearch
from app.core.exceptions import ConflictError, NotFoundError

class PathologistRepository:
    """Repositorio para operaciones CRUD de Pathologists"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.pathologists

    def _convert_doc_to_response(self, doc: dict) -> dict:
        """Convertir documento de MongoDB a formato de respuesta"""
        if doc:
            doc["id"] = str(doc["_id"])
            doc["pathologist_code"] = doc.get("pathologist_code", "")
            # Asegurar que los campos de timestamp estén presentes
            if "created_at" not in doc:
                doc["created_at"] = None
            if "updated_at" not in doc:
                doc["updated_at"] = None
        return doc

    async def create(self, pathologist: PathologistCreate) -> dict:
        """Crear un nuevo patólogo"""
        try:
            from datetime import datetime, timezone
            pathologist_data = pathologist.dict()
            pathologist_data["created_at"] = datetime.now(timezone.utc)
            pathologist_data["updated_at"] = datetime.now(timezone.utc)
            result = await self.collection.insert_one(pathologist_data)
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return self._convert_doc_to_response(created_doc)
        except DuplicateKeyError as e:
            if "pathologist_code" in str(e):
                raise ConflictError("Pathologist code already exists")
            elif "pathologist_email" in str(e):
                raise ConflictError("Email already exists")
            elif "medical_license" in str(e):
                raise ConflictError("Medical license already exists")
            else:
                raise ConflictError("Duplicate key error")

    async def get_by_pathologist_code(self, pathologist_code: str) -> Optional[dict]:
        """Obtener patólogo por código"""
        doc = await self.collection.find_one({"pathologist_code": pathologist_code})
        return self._convert_doc_to_response(doc) if doc else None

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Obtener patólogo por email"""
        doc = await self.collection.find_one({"pathologist_email": email})
        return self._convert_doc_to_response(doc) if doc else None

    async def get_by_medical_license(self, medical_license: str) -> Optional[dict]:
        """Obtener patólogo por licencia médica"""
        doc = await self.collection.find_one({"medical_license": medical_license})
        return self._convert_doc_to_response(doc) if doc else None

    async def list_active(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Listar patólogos activos"""
        cursor = self.collection.find({"is_active": True}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def search(self, search_params: PathologistSearch, skip: int = 0, limit: int = 100) -> List[dict]:
        """Buscar patólogos"""
        filter_dict: Dict[str, Any] = {}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"pathologist_name": {"$regex": search_params.q, "$options": "i"}},
                {"pathologist_code": {"$regex": search_params.q, "$options": "i"}},
                {"pathologist_email": {"$regex": search_params.q, "$options": "i"}},
                {"medical_license": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos
            if search_params.pathologist_name:
                filter_dict["pathologist_name"] = {"$regex": search_params.pathologist_name, "$options": "i"}
            if search_params.pathologist_code:
                filter_dict["pathologist_code"] = search_params.pathologist_code
            if search_params.pathologist_email:
                filter_dict["pathologist_email"] = {"$regex": search_params.pathologist_email, "$options": "i"}
            if search_params.medical_license:
                filter_dict["medical_license"] = {"$regex": search_params.medical_license, "$options": "i"}
        
        # Filtro de estado activo
        if search_params.is_active is not None:
            filter_dict["is_active"] = search_params.is_active
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def update_by_pathologist_code(self, pathologist_code: str, update_data: Dict[str, Any]) -> Optional[dict]:
        """Actualizar patólogo por código"""
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"pathologist_code": pathologist_code},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_pathologist_code(pathologist_code)
        return None

    async def delete_by_pathologist_code(self, pathologist_code: str) -> bool:
        """Eliminar patólogo por código"""
        result = await self.collection.delete_one({"pathologist_code": pathologist_code})
        return result.deleted_count > 0