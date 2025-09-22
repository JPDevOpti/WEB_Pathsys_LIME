"""Repositorio para operaciones CRUD de Billing"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from ..schemas import BillingCreate, BillingUpdate, BillingSearch
from app.core.exceptions import ConflictError, NotFoundError

class BillingRepository:
    """Repositorio para operaciones CRUD de Billing"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.billing

    def _convert_doc_to_response(self, doc: dict) -> dict:
        """Convertir documento de MongoDB a formato de respuesta"""
        if doc:
            doc["id"] = str(doc["_id"])
            doc["billing_code"] = doc.get("billing_code", "")
            # Asegurar que los campos de timestamp estén presentes
            if "created_at" not in doc:
                doc["created_at"] = None
            if "updated_at" not in doc:
                doc["updated_at"] = None
        return doc

    async def create(self, billing: BillingCreate) -> dict:
        """Crear un nuevo usuario de facturación"""
        try:
            from datetime import datetime, timezone
            billing_data = billing.dict()
            billing_data["created_at"] = datetime.now(timezone.utc)
            billing_data["updated_at"] = datetime.now(timezone.utc)
            result = await self.collection.insert_one(billing_data)
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            return self._convert_doc_to_response(created_doc)
        except DuplicateKeyError as e:
            if "billing_code" in str(e):
                raise ConflictError("Billing code already exists")
            elif "billing_email" in str(e):
                raise ConflictError("Email already exists")
            else:
                raise ConflictError("Duplicate key error")

    async def get_by_billing_code(self, billing_code: str) -> Optional[dict]:
        """Obtener usuario de facturación por código"""
        doc = await self.collection.find_one({"billing_code": billing_code})
        return self._convert_doc_to_response(doc) if doc else None

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Obtener usuario de facturación por email"""
        doc = await self.collection.find_one({"billing_email": email})
        return self._convert_doc_to_response(doc) if doc else None

    async def list_active(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Listar usuarios de facturación activos"""
        cursor = self.collection.find({"is_active": True}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def search(self, search_params: BillingSearch, skip: int = 0, limit: int = 100) -> List[dict]:
        """Buscar usuarios de facturación"""
        filter_dict: Dict[str, Any] = {}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"billing_name": {"$regex": search_params.q, "$options": "i"}},
                {"billing_code": {"$regex": search_params.q, "$options": "i"}},
                {"billing_email": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos
            if search_params.billing_name:
                filter_dict["billing_name"] = {"$regex": search_params.billing_name, "$options": "i"}
            if search_params.billing_code:
                filter_dict["billing_code"] = search_params.billing_code
            if search_params.billing_email:
                filter_dict["billing_email"] = {"$regex": search_params.billing_email, "$options": "i"}
        
        # Filtro de estado activo
        if search_params.is_active is not None:
            filter_dict["is_active"] = search_params.is_active
        
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(doc) for doc in docs]

    async def update_by_billing_code(self, billing_code: str, update_data: Dict[str, Any]) -> Optional[dict]:
        """Actualizar usuario de facturación por código"""
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"billing_code": billing_code},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_billing_code(billing_code)
        return None

    async def delete_by_billing_code(self, billing_code: str) -> bool:
        """Eliminar usuario de facturación por código"""
        result = await self.collection.delete_one({"billing_code": billing_code})
        return result.deleted_count > 0
