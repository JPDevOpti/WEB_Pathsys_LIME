from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.shared.repositories.base import BaseRepository
from app.modules.auxiliares.models.auxiliar import Auxiliar
from app.modules.auxiliares.schemas.auxiliar import AuxiliarSearch, AuxiliarCreate, AuxiliarUpdate

class AuxiliarRepository(BaseRepository[Auxiliar, AuxiliarCreate, AuxiliarUpdate]):
    """Repositorio para operaciones CRUD de Auxiliares"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "auxiliares", Auxiliar)
    
    async def get_by_email(self, email: str) -> Optional[Auxiliar]:
        """Obtener auxiliar por email"""
        document = await self.collection.find_one({"AuxiliarEmail": email})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[Auxiliar]:
        """Obtener auxiliar por código"""
        document = await self.collection.find_one({"auxiliarCode": codigo})
        if document:
            return self.model_class(**document)
        return None
    
    async def search_auxiliares(self, search_params: AuxiliarSearch) -> List[Auxiliar]:
        """Buscar auxiliares con filtros avanzados"""
        query: Dict[str, Any] = {"isActive": True}
        
        if search_params.auxiliarName:
            query["auxiliarName"] = {"$regex": search_params.auxiliarName, "$options": "i"}
        
        if search_params.auxiliarCode:
            query["auxiliarCode"] = {"$regex": search_params.auxiliarCode, "$options": "i"}
        
        if search_params.AuxiliarEmail:
            query["AuxiliarEmail"] = {"$regex": search_params.AuxiliarEmail, "$options": "i"}
        
        if search_params.isActive is not None:
            query["isActive"] = search_params.isActive
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_activos(self) -> List[Auxiliar]:
        """Obtener todos los auxiliares activos"""
        cursor = self.collection.find({"isActive": True})
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_inactivos(self) -> List[Auxiliar]:
        """Obtener todos los auxiliares inactivos"""
        cursor = self.collection.find({"isActive": False})
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def count_by_status(self, is_active: bool) -> int:
        """Contar auxiliares por estado"""
        return await self.collection.count_documents({"isActive": is_active})
    
    async def exists_by_email(self, email: str, exclude_id: Optional[ObjectId] = None) -> bool:
        """Verificar si existe un auxiliar con el email dado"""
        filters: Dict[str, Any] = {"AuxiliarEmail": email}
        if exclude_id:
            filters["_id"] = {"$ne": exclude_id}
        
        result = await self.collection.find_one(filters)
        return result is not None
    
    async def exists_by_codigo(self, codigo: str, exclude_id: Optional[ObjectId] = None) -> bool:
        """Verificar si existe un auxiliar con el código dado"""
        filters: Dict[str, Any] = {"auxiliarCode": codigo}
        if exclude_id:
            filters["_id"] = {"$ne": exclude_id}
        
        result = await self.collection.find_one(filters)
        return result is not None
    
    async def soft_delete_by_codigo(self, codigo: str) -> bool:
        """Eliminación suave por código"""
        result = await self.collection.update_one(
            {"auxiliarCode": codigo, "isActive": True},
            {
                "$set": {
                    "isActive": False,
                    "fecha_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def hard_delete_by_codigo(self, codigo: str) -> bool:
        """Eliminación física por código"""
        result = await self.collection.delete_one({"auxiliarCode": codigo})
        return result.deleted_count > 0
    
    async def create_auxiliar_from_schema(self, obj_in: AuxiliarCreate) -> Auxiliar:
        """Crear un auxiliar excluyendo el campo password del esquema"""
        # Convertir a diccionario y excluir password
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False, exclude={'password'})
        else:
            obj_data = obj_in.dict(by_alias=False, exclude={'password'})
        
        obj_data["fecha_creacion"] = datetime.utcnow()
        obj_data["fecha_actualizacion"] = datetime.utcnow()
        # Asegurar que isActive esté presente si no se especifica
        if "isActive" not in obj_data:
            obj_data["isActive"] = True
        
        try:
            result = await self.collection.insert_one(obj_data)
            created_obj = await self.collection.find_one({"_id": result.inserted_id})
            if created_obj:
                return self.model_class(**created_obj)
            else:
                raise ValueError("Failed to create document")
        except Exception as e:
            raise e

    async def activate_by_codigo(self, codigo: str) -> bool:
        """Activar auxiliar por código"""
        result = await self.collection.update_one(
            {"auxiliarCode": codigo, "isActive": False},
            {
                "$set": {
                    "isActive": True,
                    "fecha_actualizacion": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0