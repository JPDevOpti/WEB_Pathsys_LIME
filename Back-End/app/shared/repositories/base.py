"""Clase base para repositorios."""

from typing import TypeVar, Generic, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone

T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema')
UpdateSchema = TypeVar('UpdateSchema')

class BaseRepository(Generic[T, CreateSchema, UpdateSchema]):
    """Clase base para repositorios con operaciones CRUD básicas."""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str, model_class: type):
        self.database = database
        self.collection = database[collection_name]
        self.model_class = model_class

    def _normalize_boolean_fields_for_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar campos booleanos para escritura."""
        # Por defecto, no hacer nada. Los repositorios específicos pueden sobrescribir esto.
        return data

    async def create(self, obj_in: Any) -> T:
        """Crear un nuevo objeto."""
        if isinstance(obj_in, dict):
            obj_data = dict(obj_in)
        elif hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False)
        else:
            obj_data = obj_in.dict(by_alias=False)
        
        obj_data.setdefault("created_at", datetime.now(timezone.utc))
        obj_data["updated_at"] = datetime.now(timezone.utc)
        
        # Normalizar campos booleanos
        obj_data = self._normalize_boolean_fields_for_write(obj_data)
        
        try:
            result = await self.collection.insert_one(obj_data)
            created_obj = await self.collection.find_one({"_id": result.inserted_id})
            if created_obj:
                return self.model_class(**created_obj)
            else:
                raise ValueError("Error al recuperar el objeto creado")
        except Exception as e:
            raise ValueError(f"Error al crear el objeto: {str(e)}")

    async def get(self, id: Any) -> Optional[T]:
        """Obtener un objeto por ID."""
        try:
            from bson import ObjectId
            if isinstance(id, str):
                id = ObjectId(id)
            document = await self.collection.find_one({"_id": id})
            if document:
                return self.model_class(**document)
            return None
        except Exception as e:
            raise ValueError(f"Error al obtener el objeto: {str(e)}")

    async def update(self, id: Any, obj_in: UpdateSchema) -> Optional[T]:
        """Actualizar un objeto existente."""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(by_alias=False, exclude_unset=True)
        else:
            update_data = obj_in.dict(by_alias=False, exclude_unset=True)
        
        if not update_data:
            return await self.get(id)
        
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_data = self._normalize_boolean_fields_for_write(update_data)
        
        try:
            from bson import ObjectId
            if isinstance(id, str):
                id = ObjectId(id)
            
            result = await self.collection.find_one_and_update(
                {"_id": id},
                {"$set": update_data},
                return_document=True
            )
            if result:
                return self.model_class(**result)
            return None
        except Exception as e:
            raise ValueError(f"Error al actualizar el objeto: {str(e)}")

    async def delete(self, id: Any) -> bool:
        """Eliminar un objeto."""
        try:
            from bson import ObjectId
            if isinstance(id, str):
                id = ObjectId(id)
            
            result = await self.collection.delete_one({"_id": id})
            return result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Error al eliminar el objeto: {str(e)}")

    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Listar objetos con paginación."""
        try:
            cursor = self.collection.find({}).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            return [self.model_class(**doc) for doc in documents]
        except Exception as e:
            raise ValueError(f"Error al listar objetos: {str(e)}")

    async def count(self) -> int:
        """Contar objetos."""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            raise ValueError(f"Error al contar objetos: {str(e)}")
