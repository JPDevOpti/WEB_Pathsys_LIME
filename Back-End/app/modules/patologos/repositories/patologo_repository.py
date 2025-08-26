"""Repositorio para operaciones CRUD de Patólogos"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.shared.repositories.base import BaseRepository
from app.modules.patologos.models.patologo import Patologo
from app.modules.patologos.schemas.patologo import PatologoSearch, PatologoCreate, PatologoUpdate

class PatologoRepository(BaseRepository[Patologo, PatologoCreate, PatologoUpdate]):
    """Repositorio para operaciones CRUD de Patólogos"""
    
    def __init__(self, database: Any):
        super().__init__(database, "patologos", Patologo)
    
    async def get_by_email(self, email: str) -> Optional[Patologo]:
        """Obtener patólogo por email"""
        document = await self.collection.find_one({"PatologoEmail": email})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[Patologo]:
        """Obtener patólogo por código"""
        document = await self.collection.find_one({"patologoCode": codigo})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_registro_medico(self, registro_medico: str) -> Optional[Patologo]:
        """Obtener patólogo por registro médico"""
        document = await self.collection.find_one({"registro_medico": registro_medico})
        if document:
            return self.model_class(**document)
        return None
    

    
    async def search(self, search_params: PatologoSearch, skip: int = 0, limit: int = 100) -> List[Patologo]:
        """Búsqueda avanzada de patólogos"""
        filter_dict: Dict[str, Any] = {}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"patologoName": {"$regex": search_params.q, "$options": "i"}},
                {"patologoCode": {"$regex": search_params.q, "$options": "i"}},
                {"PatologoEmail": {"$regex": search_params.q, "$options": "i"}},
                {"registro_medico": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos de texto (búsqueda parcial)
            if search_params.patologoName:
                filter_dict["patologoName"] = {"$regex": search_params.patologoName, "$options": "i"}
            if search_params.PatologoEmail:
                filter_dict["PatologoEmail"] = {"$regex": search_params.PatologoEmail, "$options": "i"}
            if search_params.patologoCode:
                filter_dict["patologoCode"] = search_params.patologoCode
            if search_params.registro_medico:
                filter_dict["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        # Filtros exactos
        if search_params.isActive is not None:
            filter_dict["isActive"] = search_params.isActive
        
        return await self.get_multi(skip=skip, limit=limit, filters=filter_dict)
    

    
    async def create_patologo_from_schema(self, obj_in: PatologoCreate) -> Patologo:
        """Crear un patólogo excluyendo el campo password del esquema"""
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
    
    async def toggle_estado(self, patologo_id: str) -> Optional[Patologo]:
        """Cambiar estado activo/inactivo de un patólogo"""
        patologo = await self.get(patologo_id)
        if not patologo:
            return None
        
        new_state = not patologo.isActive
        update_data = {"isActive": new_state, "fecha_actualizacion": datetime.utcnow()}
        return await self.update(patologo_id, update_data)