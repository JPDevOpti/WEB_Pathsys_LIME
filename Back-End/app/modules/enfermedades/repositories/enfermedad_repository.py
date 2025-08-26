from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.modules.enfermedades.models.enfermedad import EnfermedadCreate, EnfermedadUpdate, EnfermedadInDB


class EnfermedadRepository:
    """Repositorio para operaciones de enfermedades"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.enfermedades
    
    def _convert_objectid_to_string(self, doc: dict) -> dict:
        """Convierte ObjectId a string en el documento"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def create(self, enfermedad: EnfermedadCreate) -> EnfermedadInDB:
        """Crear una nueva enfermedad"""
        enfermedad_dict = enfermedad.model_dump()
        enfermedad_dict["created_at"] = datetime.utcnow()
        enfermedad_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(enfermedad_dict)
        enfermedad_dict["_id"] = str(result.inserted_id)
        
        return EnfermedadInDB(**enfermedad_dict)
    
    async def get_by_id(self, enfermedad_id: str) -> Optional[EnfermedadInDB]:
        """Obtener enfermedad por ID"""
        try:
            obj_id = ObjectId(enfermedad_id)
            document = await self.collection.find_one({"_id": obj_id})
            if document:
                document = self._convert_objectid_to_string(document)
                return EnfermedadInDB(**document)
            return None
        except Exception:
            return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[EnfermedadInDB]:
        """Obtener enfermedad por código"""
        document = await self.collection.find_one({"codigo": codigo})
        if document:
            document = self._convert_objectid_to_string(document)
            return EnfermedadInDB(**document)
        return None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[EnfermedadInDB]:
        """Obtener todas las enfermedades con paginación"""
        filter_query = {}
        if is_active is not None:
            filter_query["isActive"] = is_active
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        # Convertir documentos y crear instancias de EnfermedadInDB
        enfermedades = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                enfermedad = EnfermedadInDB(**doc)
                enfermedades.append(enfermedad)
            except Exception as e:
                print(f"Error al convertir documento: {e}")
                print(f"Documento: {doc}")
                continue
        
        return enfermedades
    
    async def search_by_name(
        self, 
        nombre: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[EnfermedadInDB]:
        """Buscar enfermedades por nombre"""
        filter_query = {
            "nombre": {"$regex": nombre, "$options": "i"},
            "isActive": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        enfermedades = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                enfermedad = EnfermedadInDB(**doc)
                enfermedades.append(enfermedad)
            except Exception as e:
                print(f"Error al convertir documento: {e}")
                continue
        
        return enfermedades
    
    async def search_by_codigo(
        self, 
        codigo: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[EnfermedadInDB]:
        """Buscar enfermedades por código"""
        filter_query = {
            "codigo": {"$regex": codigo, "$options": "i"},
            "isActive": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        enfermedades = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                enfermedad = EnfermedadInDB(**doc)
                enfermedades.append(enfermedad)
            except Exception as e:
                print(f"Error al convertir documento: {e}")
                continue
        
        return enfermedades
    
    async def get_by_tabla(
        self, 
        tabla: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[EnfermedadInDB]:
        """Obtener enfermedades por tabla de referencia"""
        filter_query = {
            "tabla": tabla,
            "isActive": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        enfermedades = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                enfermedad = EnfermedadInDB(**doc)
                enfermedades.append(enfermedad)
            except Exception as e:
                print(f"Error al convertir documento: {e}")
                continue
        
        return enfermedades
    
    async def update(
        self, 
        enfermedad_id: str, 
        enfermedad_update: EnfermedadUpdate
    ) -> Optional[EnfermedadInDB]:
        """Actualizar una enfermedad"""
        try:
            obj_id = ObjectId(enfermedad_id)
            update_data = enfermedad_update.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": obj_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_by_id(enfermedad_id)
            return None
        except Exception:
            return None
    
    async def delete(self, enfermedad_id: str) -> bool:
        """Eliminar una enfermedad (soft delete)"""
        try:
            obj_id = ObjectId(enfermedad_id)
            result = await self.collection.update_one(
                {"_id": obj_id},
                {"$set": {"isActive": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def hard_delete(self, enfermedad_id: str) -> bool:
        """Eliminar una enfermedad permanentemente"""
        try:
            obj_id = ObjectId(enfermedad_id)
            result = await self.collection.delete_one({"_id": obj_id})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def count_total(self, is_active: Optional[bool] = None) -> int:
        """Contar total de enfermedades"""
        filter_query = {}
        if is_active is not None:
            filter_query["isActive"] = is_active
        
        return await self.collection.count_documents(filter_query)
    
    async def exists_by_codigo(self, codigo: str) -> bool:
        """Verificar si existe una enfermedad con el código dado"""
        count = await self.collection.count_documents({"codigo": codigo})
        return count > 0
