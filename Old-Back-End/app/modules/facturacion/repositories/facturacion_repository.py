from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.shared.repositories.base import BaseRepository
from app.modules.facturacion.models.facturacion import Facturacion
from app.modules.facturacion.schemas.facturacion import FacturacionSearch, FacturacionCreate, FacturacionUpdate

class FacturacionRepository(BaseRepository[Facturacion, FacturacionCreate, FacturacionUpdate]):
    """Repositorio para operaciones CRUD de Facturación"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "facturacion", Facturacion)
    
    async def get_by_email(self, email: str) -> Optional[Facturacion]:
        """Obtener usuario de facturación por email"""
        document = await self.collection.find_one({"facturacion_email": email})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[Facturacion]:
        """Obtener usuario de facturación por código"""
        document = await self.collection.find_one({"facturacion_code": codigo})
        if document:
            return self.model_class(**document)
        return None
    
    async def search_facturacion(self, search_params: FacturacionSearch) -> List[Facturacion]:
        """Buscar usuarios de facturación con filtros avanzados"""
        query: Dict[str, Any] = {}
        
        if (search_params.facturacion_name and search_params.facturacion_code and 
            search_params.facturacion_email and search_params.facturacion_name == search_params.facturacion_code == search_params.facturacion_email):
            search_term = search_params.facturacion_name
            query["$or"] = [
                {"facturacion_name": {"$regex": search_term, "$options": "i"}},
                {"facturacion_code": {"$regex": search_term, "$options": "i"}},
                {"facturacion_email": {"$regex": search_term, "$options": "i"}}
            ]
        else:
            if search_params.facturacion_name:
                query["facturacion_name"] = {"$regex": search_params.facturacion_name, "$options": "i"}
            
            if search_params.facturacion_code:
                query["facturacion_code"] = {"$regex": search_params.facturacion_code, "$options": "i"}
            
            if search_params.facturacion_email:
                query["facturacion_email"] = {"$regex": search_params.facturacion_email, "$options": "i"}
        
        if search_params.is_active is not None:
            query["is_active"] = search_params.is_active
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]

    async def search_active_facturacion(self, search_params: FacturacionSearch) -> List[Facturacion]:
        """Buscar solo usuarios de facturación activos con filtros"""
        query: Dict[str, Any] = {"is_active": True}
        
        if (search_params.facturacion_name and search_params.facturacion_code and 
            search_params.facturacion_email and search_params.facturacion_name == search_params.facturacion_code == search_params.facturacion_email):
            search_term = search_params.facturacion_name
            query["$or"] = [
                {"facturacion_name": {"$regex": search_term, "$options": "i"}},
                {"facturacion_code": {"$regex": search_term, "$options": "i"}},
                {"facturacion_email": {"$regex": search_term, "$options": "i"}}
            ]
        else:
            if search_params.facturacion_name:
                query["facturacion_name"] = {"$regex": search_params.facturacion_name, "$options": "i"}
            
            if search_params.facturacion_code:
                query["facturacion_code"] = {"$regex": search_params.facturacion_code, "$options": "i"}
            
            if search_params.facturacion_email:
                query["facturacion_email"] = {"$regex": search_params.facturacion_email, "$options": "i"}
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]

    async def search_all_facturacion_including_inactive(self, search_params: FacturacionSearch) -> List[Facturacion]:
        """Buscar todos los usuarios de facturación incluyendo inactivos"""
        query: Dict[str, Any] = {}
        
        if (search_params.facturacion_name and search_params.facturacion_code and 
            search_params.facturacion_email and search_params.facturacion_name == search_params.facturacion_code == search_params.facturacion_email):
            search_term = search_params.facturacion_name
            query["$or"] = [
                {"facturacion_name": {"$regex": search_term, "$options": "i"}},
                {"facturacion_code": {"$regex": search_term, "$options": "i"}},
                {"facturacion_email": {"$regex": search_term, "$options": "i"}}
            ]
        else:
            if search_params.facturacion_name:
                query["facturacion_name"] = {"$regex": search_params.facturacion_name, "$options": "i"}
            
            if search_params.facturacion_code:
                query["facturacion_code"] = {"$regex": search_params.facturacion_code, "$options": "i"}
            
            if search_params.facturacion_email:
                query["facturacion_email"] = {"$regex": search_params.facturacion_email, "$options": "i"}
        
        cursor = self.collection.find(query)
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_activos(self) -> List[Facturacion]:
        """Obtener todos los usuarios de facturación activos"""
        cursor = self.collection.find({"is_active": True})
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_inactivos(self) -> List[Facturacion]:
        """Obtener todos los usuarios de facturación inactivos"""
        cursor = await self.collection.find({"is_active": False})
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def count_by_status(self, is_active: bool) -> int:
        """Contar usuarios de facturación por estado"""
        return await self.collection.count_documents({"is_active": is_active})
    
    async def exists_by_email(self, email: str, exclude_id: Optional[ObjectId] = None) -> bool:
        """Verificar si existe un usuario de facturación con el email dado"""
        filters: Dict[str, Any] = {"facturacion_email": email}
        if exclude_id:
            filters["_id"] = {"$ne": exclude_id}
        
        result = await self.collection.find_one(filters)
        return result is not None
    
    async def exists_by_codigo(self, codigo: str, exclude_id: Optional[ObjectId] = None) -> bool:
        """Verificar si existe un usuario de facturación con el código dado"""
        filters: Dict[str, Any] = {"facturacion_code": codigo}
        if exclude_id:
            filters["_id"] = {"$ne": exclude_id}
        
        result = await self.collection.find_one(filters)
        return result is not None
    
    async def soft_delete_by_codigo(self, codigo: str) -> bool:
        """Eliminación suave por código"""
        result = await self.collection.update_one(
            {"facturacion_code": codigo, "is_active": True},
            {
                "$set": {
                    "is_active": False,
                    "fecha_actualizacion": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0
    
    async def hard_delete_by_codigo(self, codigo: str) -> bool:
        """Eliminación física por código"""
        result = await self.collection.delete_one({"facturacion_code": codigo})
        return result.deleted_count > 0
    
    async def create_facturacion_from_schema(self, obj_in: FacturacionCreate) -> Facturacion:
        """Crear un usuario de facturación excluyendo el campo password del esquema"""
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False, exclude={'password'})
        else:
            obj_data = obj_in.dict(by_alias=False, exclude={'password'})
        
        obj_data["fecha_creacion"] = datetime.now(timezone.utc)
        obj_data["fecha_actualizacion"] = datetime.now(timezone.utc)
        if "is_active" not in obj_data:
            obj_data["is_active"] = True
        
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
        """Activar usuario de facturación por código"""
        result = await self.collection.update_one(
            {"facturacion_code": codigo, "is_active": False},
            {
                "$set": {
                    "is_active": True,
                    "fecha_actualizacion": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0
