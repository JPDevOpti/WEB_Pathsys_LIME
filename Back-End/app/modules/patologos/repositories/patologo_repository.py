"""Repositorio para operaciones CRUD de Patólogos"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
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
        document = await self.collection.find_one({"patologo_email": email})
        if document:
            return self.model_class(**document)
        return None
    
    async def get_by_codigo(self, codigo: str) -> Optional[Patologo]:
        """Obtener patólogo por código"""
        document = await self.collection.find_one({"patologo_code": codigo})
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
                {"patologo_name": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_code": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_email": {"$regex": search_params.q, "$options": "i"}},
                {"registro_medico": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos de texto (búsqueda parcial)
            if search_params.patologo_name:
                filter_dict["patologo_name"] = {"$regex": search_params.patologo_name, "$options": "i"}
            if search_params.patologo_email:
                filter_dict["patologo_email"] = {"$regex": search_params.patologo_email, "$options": "i"}
            if search_params.patologo_code:
                filter_dict["patologo_code"] = search_params.patologo_code
            if search_params.registro_medico:
                filter_dict["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        # Filtros exactos
        if search_params.is_active is not None:
            filter_dict["is_active"] = search_params.is_active
        
        return await self.get_multi(skip=skip, limit=limit, filters=filter_dict)

    async def search_active(self, search_params: PatologoSearch, skip: int = 0, limit: int = 100) -> List[Patologo]:
        """Búsqueda de solo patólogos activos"""
        filter_dict: Dict[str, Any] = {"is_active": True}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"patologo_name": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_code": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_email": {"$regex": search_params.q, "$options": "i"}},
                {"registro_medico": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos de texto (búsqueda parcial)
            if search_params.patologo_name:
                filter_dict["patologo_name"] = {"$regex": search_params.patologo_name, "$options": "i"}
            if search_params.patologo_email:
                filter_dict["patologo_email"] = {"$regex": search_params.patologo_email, "$options": "i"}
            if search_params.patologo_code:
                filter_dict["patologo_code"] = search_params.patologo_code
            if search_params.registro_medico:
                filter_dict["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        return await self.get_multi(skip=skip, limit=limit, filters=filter_dict)

    async def search_all_including_inactive(self, search_params: PatologoSearch, skip: int = 0, limit: int = 100) -> List[Patologo]:
        """Búsqueda de todos los patólogos incluyendo inactivos"""
        filter_dict: Dict[str, Any] = {}
        
        # Búsqueda general con parámetro 'q'
        if search_params.q:
            filter_dict["$or"] = [
                {"patologo_name": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_code": {"$regex": search_params.q, "$options": "i"}},
                {"patologo_email": {"$regex": search_params.q, "$options": "i"}},
                {"registro_medico": {"$regex": search_params.q, "$options": "i"}}
            ]
        else:
            # Filtros específicos de texto (búsqueda parcial)
            if search_params.patologo_name:
                filter_dict["patologo_name"] = {"$regex": search_params.patologo_name, "$options": "i"}
            if search_params.patologo_email:
                filter_dict["patologo_email"] = {"$regex": search_params.patologo_email, "$options": "i"}
            if search_params.patologo_code:
                filter_dict["patologo_code"] = search_params.patologo_code
            if search_params.registro_medico:
                filter_dict["registro_medico"] = {"$regex": search_params.registro_medico, "$options": "i"}
        
        return await self.get_multi(skip=skip, limit=limit, filters=filter_dict)
    

    
    async def create_patologo_from_schema(self, obj_in: PatologoCreate) -> Patologo:
        """Crear un patólogo excluyendo el campo password del esquema"""
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
    
    async def toggle_estado(self, patologo_id: str) -> Optional[Patologo]:
        """Cambiar estado activo/inactivo de un patólogo"""
        patologo = await self.get(patologo_id)
        if not patologo:
            return None
        
        new_state = not patologo.is_active
        update_data = {"is_active": new_state, "fecha_actualizacion": datetime.now(timezone.utc)}
        return await self.update(patologo_id, update_data)
    
    async def update_firma(self, patologo_id: str, firma: str) -> Optional[Patologo]:
        """Actualizar la firma digital de un patólogo"""
        update_data = {"firma": firma, "fecha_actualizacion": datetime.now(timezone.utc)}
        return await self.update(patologo_id, update_data)