"""Repositorio base para operaciones CRUD genéricas"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

# Tipos genéricos
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repositorio base con operaciones CRUD genéricas"""
    
    def __init__(
        self, 
        database: AsyncIOMotorDatabase, 
        collection_name: str, 
        model_class: Type[ModelType]
    ):
        self.database = database
        self.collection: AsyncIOMotorCollection = database[collection_name]
        self.model_class = model_class
        
    def _normalize_boolean_fields_for_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sincroniza claves is_active e isActive para mantener compatibilidad."""
        if "is_active" in data and "isActive" not in data:
            data["isActive"] = data["is_active"]
        elif "isActive" in data and "is_active" not in data:
            data["is_active"] = data["isActive"]
        return data

    def _normalize_boolean_filters_for_query(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Permite filtrar por is_active o isActive indistintamente."""
        query = filters.copy() if filters else {}
        if "is_active" in query and "isActive" not in query:
            value = query.pop("is_active")
            query["$or"] = query.get("$or", []) + [{"is_active": value}, {"isActive": value}]
        elif "isActive" in query and "is_active" not in query:
            value = query.pop("isActive")
            query["$or"] = query.get("$or", []) + [{"is_active": value}, {"isActive": value}]
        return query
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo documento"""
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False)
        else:
            obj_data = obj_in.dict(by_alias=False)
        
        obj_data.setdefault("fecha_creacion", datetime.utcnow())
        obj_data["fecha_actualizacion"] = datetime.utcnow()
        if "is_active" not in obj_data and "isActive" not in obj_data:
            obj_data["is_active"] = True
        obj_data = self._normalize_boolean_fields_for_write(obj_data)
        
        try:
            result = await self.collection.insert_one(obj_data)
            created_obj = await self.collection.find_one({"_id": result.inserted_id})
            if created_obj:
                return self.model_class(**created_obj)
            else:
                raise ValueError("Failed to create document")
        except Exception as e:
            raise e
    
    async def get(self, id: str) -> Optional[ModelType]:
        """Obtener documento por ID"""
        if not ObjectId.is_valid(id):
            return None
        
        document = await self.collection.find_one({"_id": ObjectId(id)})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Obtener múltiples documentos"""
        query = self._normalize_boolean_filters_for_query(filters)
        cursor = self.collection.find(query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in documents]
    
    async def update(self, id: str, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Actualizar documento por ID"""
        if not ObjectId.is_valid(id):
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True, exclude_none=True, by_alias=False)
        if update_data:
            update_data["fecha_actualizacion"] = datetime.utcnow()
            update_data = self._normalize_boolean_fields_for_write(update_data)
            
            await self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
        
        return await self.get(id)
    
    async def delete(self, id: str) -> bool:
        """Eliminar documento por ID"""
        if not ObjectId.is_valid(id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar documentos"""
        query = filters or {}
        return await self.collection.count_documents(query)
    
    async def exists(self, id: str) -> bool:
        """Verificar si existe un documento por ID"""
        if not ObjectId.is_valid(id):
            return False
        
        count = await self.collection.count_documents({"_id": ObjectId(id)})
        return count > 0