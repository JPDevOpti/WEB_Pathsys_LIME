from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.modules.entidades.models.entidad import (
    Entidad,
    EntidadCreate,
    EntidadUpdate,
    EntidadSearch
)


class EntidadRepository:
    """Repositorio para operaciones de entidades en MongoDB"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.entidades
    
    def _convert_objectid_to_string(self, doc: dict) -> dict:
        """Convierte ObjectId a string en el documento"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def create(self, entidad_data: EntidadCreate) -> Entidad:
        """Crear una nueva entidad"""
        entidad_dict = entidad_data.model_dump()
        entidad_dict["fecha_creacion"] = datetime.utcnow()
        
        result = await self.collection.insert_one(entidad_dict)
        entidad_dict["_id"] = str(result.inserted_id)  # Convertir ObjectId a string
        
        return Entidad(**entidad_dict)

    async def get_by_code(self, code: str) -> Optional[Entidad]:
        """Obtener entidad por código"""
        entidad_doc = await self.collection.find_one({"EntidadCode": code})
        if entidad_doc:
            entidad_doc = self._convert_objectid_to_string(entidad_doc)
            return Entidad(**entidad_doc)
        return None

    async def get_by_code_including_inactive(self, code: str) -> Optional[Entidad]:
        """Obtener entidad por código incluyendo inactivas (para uso interno)"""
        entidad_doc = await self.collection.find_one({"EntidadCode": code})
        if entidad_doc:
            entidad_doc = self._convert_objectid_to_string(entidad_doc)
            return Entidad(**entidad_doc)
        return None
    
    async def get_all(self, search_params: EntidadSearch) -> List[Entidad]:
        """Obtener todas las entidades con filtros"""
        filter_dict = {}
        
        # Aplicar filtros
        if search_params.query:
            filter_dict["$or"] = [
                {"EntidadName": {"$regex": search_params.query, "$options": "i"}},
                {"EntidadCode": {"$regex": search_params.query, "$options": "i"}},
                {"observaciones": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        if search_params.activo is not None:
            filter_dict["isActive"] = search_params.activo
        
        cursor = self.collection.find(filter_dict)
        cursor = cursor.skip(search_params.skip).limit(search_params.limit)
        
        entidades = []
        async for doc in cursor:
            doc = self._convert_objectid_to_string(doc)
            entidades.append(Entidad(**doc))
        
        return entidades
    
    async def update_by_code(self, code: str, entidad_update: EntidadUpdate) -> Optional[Entidad]:
        """Actualizar una entidad por código"""
        update_data = entidad_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_code(code)
        
        update_data["fecha_actualizacion"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"EntidadCode": code},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_by_code(code)
        return None
    
    async def delete_by_code(self, code: str) -> bool:
        """Eliminar una entidad por código (eliminación permanente)"""
        result = await self.collection.delete_one({"EntidadCode": code})
        return result.deleted_count > 0

    async def toggle_active_by_code(self, code: str, new_active_state: bool) -> bool:
        """Cambiar estado activo de una entidad por código"""
        update_data = {
            "isActive": new_active_state,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"EntidadCode": code},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def count(self, search_params: EntidadSearch) -> int:
        """Contar entidades con filtros"""
        filter_dict = {}
        
        if search_params.query:
            filter_dict["$or"] = [
                {"EntidadName": {"$regex": search_params.query, "$options": "i"}},
                {"EntidadCode": {"$regex": search_params.query, "$options": "i"}},
                {"observaciones": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        if search_params.activo is not None:
            filter_dict["isActive"] = search_params.activo
        
        return await self.collection.count_documents(filter_dict)