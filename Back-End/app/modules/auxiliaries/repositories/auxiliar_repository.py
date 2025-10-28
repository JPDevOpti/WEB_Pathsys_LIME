"""Repositorio para operaciones CRUD de Auxiliaries"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from ..schemas import AuxiliarCreate, AuxiliarUpdate, AuxiliarSearch
from app.core.exceptions import ConflictError, NotFoundError

class AuxiliarRepository:
    """Repositorio para operaciones CRUD de Auxiliaries"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.auxiliaries

    def _convert_doc_to_response(self, doc: dict) -> dict:
        """Convertir documento de MongoDB a formato de respuesta"""
        if doc:
            doc["id"] = str(doc["_id"])
            doc["auxiliar_code"] = doc.get("auxiliar_code", "")
            # Asegurar que los campos de timestamp estén presentes
            if "created_at" not in doc:
                doc["created_at"] = None
            if "updated_at" not in doc:
                doc["updated_at"] = None
        return doc

    async def create(self, auxiliar: AuxiliarCreate) -> dict:
        """Crear un nuevo auxiliar"""
        try:
            from datetime import datetime, timezone
            auxiliar_data = auxiliar.model_dump()
            auxiliar_data["created_at"] = datetime.now(timezone.utc)
            auxiliar_data["updated_at"] = datetime.now(timezone.utc)
            result = await self.collection.insert_one(auxiliar_data)
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return self._convert_doc_to_response(created_doc)
        except DuplicateKeyError as e:
            if "auxiliar_code" in str(e):
                raise ConflictError("Auxiliar code already exists")
            elif "auxiliar_email" in str(e):
                raise ConflictError("Email already exists")
            else:
                raise ConflictError("Duplicate key error")

    async def get_by_auxiliar_code(self, auxiliar_code: str) -> Optional[dict]:
        """Obtener auxiliar por código"""
        doc = await self.collection.find_one({"auxiliar_code": auxiliar_code})
        return self._convert_doc_to_response(doc) if doc else None

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Obtener auxiliar por email"""
        doc = await self.collection.find_one({"auxiliar_email": email})
        return self._convert_doc_to_response(doc) if doc else None

    async def list_active(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Listar auxiliares activos"""
        cursor = self.collection.find({"is_active": True}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def search(self, search_params: AuxiliarSearch, skip: int = 0, limit: int = 100) -> List[dict]:
        """Buscar auxiliares"""
        filter_dict: Dict[str, Any] = {}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"auxiliar_name": {"$regex": search_params.q, "$options": "i"}},
                {"auxiliar_code": {"$regex": search_params.q, "$options": "i"}},
                {"auxiliar_email": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos
            if search_params.auxiliar_name:
                filter_dict["auxiliar_name"] = {"$regex": search_params.auxiliar_name, "$options": "i"}
            if search_params.auxiliar_code:
                filter_dict["auxiliar_code"] = search_params.auxiliar_code
            if search_params.auxiliar_email:
                filter_dict["auxiliar_email"] = {"$regex": search_params.auxiliar_email, "$options": "i"}
        
        # Filtro de estado activo
        if search_params.is_active is not None:
            filter_dict["is_active"] = search_params.is_active
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def update_by_auxiliar_code(self, auxiliar_code: str, update_data: Dict[str, Any]) -> Optional[dict]:
        """Actualizar auxiliar por código"""
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"auxiliar_code": auxiliar_code},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_auxiliar_code(auxiliar_code)
        return None

    async def delete_by_auxiliar_code(self, auxiliar_code: str) -> bool:
        """Eliminar auxiliar por código"""
        result = await self.collection.delete_one({"auxiliar_code": auxiliar_code})
        return result.deleted_count > 0
