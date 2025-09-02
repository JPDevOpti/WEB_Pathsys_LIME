from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.shared.repositories.base import BaseRepository
from app.modules.residentes.models.residente import Residente
from app.modules.residentes.schemas.residente import ResidenteSearch, ResidenteCreate, ResidenteUpdate

class ResidenteRepository(BaseRepository[Residente, ResidenteCreate, ResidenteUpdate]):
    """Repositorio para operaciones CRUD de Residentes"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "residentes", Residente)
    
    async def get_by_email(self, email: str) -> Optional[Residente]:
        """Obtener residente por email"""
        document = await self.collection.find_one({"residente_email": email})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[Residente]:
        """Obtener residente por código"""
        document = await self.collection.find_one({"residente_code": codigo})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_registro_medico(self, registro_medico: str) -> Optional[Residente]:
        """Obtener residente por registro médico"""
        document = await self.collection.find_one({"registro_medico": registro_medico})
        if document:
            return self.model_class(**document)
        return None
    
    async def search_residentes(self, search_params: ResidenteSearch, skip: int = 0, limit: int = 10) -> List[Residente]:
        """Buscar residentes con filtros avanzados"""
        query = {}
        
        # Construir query OR para búsqueda por múltiples campos si solo se proporciona residente_name
        if search_params.residente_name and not any([
            search_params.iniciales_residente, 
            search_params.residente_code, 
            search_params.residente_email, 
            search_params.registro_medico
        ]):
            # Si solo se proporciona nombre, buscar en múltiples campos
            search_term = search_params.residente_name
            query["$or"] = [
                {"residente_name": {"$regex": search_term, "$options": "i"}},
                {"residente_code": {"$regex": search_term, "$options": "i"}},
                {"residente_email": {"$regex": search_term, "$options": "i"}},
                {"registro_medico": {"$regex": search_term, "$options": "i"}}
            ]
        else:
            # Búsqueda específica por campos individuales
            if search_params.residente_name:
                query["residente_name"] = {"$regex": search_params.residente_name, "$options": "i"}
            
            if search_params.iniciales_residente:
                query["iniciales_residente"] = {"$regex": search_params.iniciales_residente, "$options": "i"}
            
            if search_params.residente_code:
                query["residente_code"] = {"$regex": search_params.residente_code, "$options": "i"}
            
            if search_params.residente_email:
                query["residente_email"] = {"$regex": search_params.residente_email, "$options": "i"}
            
            if search_params.registro_medico:
                query["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        # Aplicar filtro de estado activo
        if search_params.is_active is not None:
            query["is_active"] = search_params.is_active
        else:
            # Por defecto, solo mostrar activos en búsquedas generales
            query["is_active"] = True
        
        cursor = self.collection.find(query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [Residente(**doc) for doc in documents]
    
    async def count_search_results(self, search_params: ResidenteSearch) -> int:
        """Contar resultados de búsqueda"""
        query = {}
        
        # Usar la misma lógica que search_residentes
        if search_params.residente_name and not any([
            search_params.iniciales_residente, 
            search_params.residente_code, 
            search_params.residente_email, 
            search_params.registro_medico
        ]):
            # Si solo se proporciona nombre, buscar en múltiples campos
            search_term = search_params.residente_name
            query["$or"] = [
                {"residente_name": {"$regex": search_term, "$options": "i"}},
                {"residente_code": {"$regex": search_term, "$options": "i"}},
                {"residente_email": {"$regex": search_term, "$options": "i"}},
                {"registro_medico": {"$regex": search_term, "$options": "i"}}
            ]
        else:
            # Búsqueda específica por campos individuales
            if search_params.residente_name:
                query["residente_name"] = {"$regex": search_params.residente_name, "$options": "i"}
            
            if search_params.iniciales_residente:
                query["iniciales_residente"] = {"$regex": search_params.iniciales_residente, "$options": "i"}
            
            if search_params.residente_code:
                query["residente_code"] = {"$regex": search_params.residente_code, "$options": "i"}
            
            if search_params.residente_email:
                query["residente_email"] = {"$regex": search_params.residente_email, "$options": "i"}
            
            if search_params.registro_medico:
                query["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        # Aplicar filtro de estado activo
        if search_params.is_active is not None:
            query["is_active"] = search_params.is_active
        else:
            # Por defecto, solo mostrar activos en búsquedas generales
            query["is_active"] = True
        
        return await self.collection.count_documents(query)
    
    async def get_by_id(self, id: str) -> Optional[Residente]:
        """Obtener residente por ID"""
        return await self.get(id)
    
    async def toggle_estado(self, residente_id: str) -> Optional[Residente]:
        """Cambiar el estado activo/inactivo de un residente"""
        residente = await self.get(residente_id)
        if not residente:
            return None
        
        # Cambiar el estado
        nuevo_estado = not residente.is_active
        
        # Crear objeto de actualización
        update_data = {"is_active": nuevo_estado, "fecha_actualizacion": datetime.now(timezone.utc)}
        
        # Actualizar en la base de datos
        result = await self.collection.update_one(
            {"_id": ObjectId(residente_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get(residente_id)
        return None
    
    async def create_residente_from_schema(self, obj_in: ResidenteCreate) -> Residente:
        """Crear un residente excluyendo el campo password del esquema"""
        # Convertir a diccionario y excluir password
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False, exclude={'password'})
        else:
            obj_data = obj_in.dict(by_alias=False, exclude={'password'})
        
        obj_data["fecha_creacion"] = datetime.now(timezone.utc)
        obj_data["fecha_actualizacion"] = datetime.now(timezone.utc)
        # Asegurar que is_active esté presente si no se especifica
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