from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone

from app.modules.pruebas.models.prueba import Prueba
from app.modules.pruebas.schemas.prueba import (
    PruebaCreate,
    PruebaUpdate,
    PruebaSearch
)


class PruebaRepository:
    """Repositorio para operaciones de pruebas en MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.pruebas
    
    async def create(self, prueba_data: PruebaCreate) -> Prueba:
        """Crear una nueva prueba"""
        prueba_dict = prueba_data.model_dump()
        prueba_dict["fecha_creacion"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(prueba_dict)
        prueba_dict["_id"] = result.inserted_id
        
        return Prueba(**prueba_dict)

    async def get_by_code(self, code: str) -> Optional[Prueba]:
        """Obtener prueba por código"""
        prueba_doc = await self.collection.find_one({"prueba_code": code})
        if prueba_doc:
            return Prueba(**prueba_doc)
        return None

    async def get_by_code_including_inactive(self, code: str) -> Optional[Prueba]:
        """Obtener prueba por código incluyendo inactivas (para uso interno)"""
        prueba_doc = await self.collection.find_one({"prueba_code": code})
        if prueba_doc:
            return Prueba(**prueba_doc)
        return None
    
    async def get_all(self, search_params: PruebaSearch) -> List[Prueba]:
        """Obtener todas las pruebas con filtros"""
        filter_dict = {}
        
        # Aplicar filtros
        if search_params.query:
            filter_dict["$or"] = [
                {"prueba_name": {"$regex": search_params.query, "$options": "i"}},
                {"prueba_code": {"$regex": search_params.query, "$options": "i"}},
                {"prueba_description": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        if search_params.activo is not None:
            filter_dict["is_active"] = search_params.activo
        
        cursor = self.collection.find(filter_dict)
        cursor = cursor.skip(search_params.skip).limit(search_params.limit)
        
        pruebas = []
        async for doc in cursor:
            pruebas.append(Prueba(**doc))
        
        return pruebas
    
    async def update_by_code(self, code: str, prueba_update: PruebaUpdate) -> Optional[Prueba]:
        """Actualizar una prueba por código"""
        update_data = prueba_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_code(code)
        
        update_data["fecha_actualizacion"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"prueba_code": code},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_by_code(code)
        return None
    
    async def delete_by_code(self, code: str) -> bool:
        """Eliminar una prueba por código (eliminación permanente)"""
        result = await self.collection.delete_one({"prueba_code": code})
        return result.deleted_count > 0

    async def toggle_active_by_code(self, code: str, new_active_state: bool) -> bool:
        """Cambiar estado activo de una prueba por código"""
        update_data = {
            "is_active": new_active_state,
            "fecha_actualizacion": datetime.now(timezone.utc)
        }
        
        result = await self.collection.update_one(
            {"prueba_code": code},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def count(self, search_params: PruebaSearch) -> int:
        """Contar pruebas con filtros"""
        filter_dict = {}
        
        if search_params.query:
            filter_dict["$or"] = [
                {"prueba_name": {"$regex": search_params.query, "$options": "i"}},
                {"prueba_code": {"$regex": search_params.query, "$options": "i"}},
                {"prueba_description": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        if search_params.activo is not None:
            filter_dict["is_active"] = search_params.activo
        
        return await self.collection.count_documents(filter_dict)