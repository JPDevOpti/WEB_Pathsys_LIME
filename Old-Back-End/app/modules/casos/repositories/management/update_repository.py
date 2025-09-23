from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.modules.casos.schemas.management.update import UpdateCaseRequest


class UpdateCaseRepository:
    """Repositorio para operaciones de actualización de casos"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.casos
    
    async def update_case(self, caso_code: str, update_data: UpdateCaseRequest) -> Optional[Dict[str, Any]]:
        """Actualizar un caso por código con TODOS los campos posibles"""
        try:
            # Preparar datos de actualización
            update_dict = update_data.dict(exclude_unset=True)
            
            # Agregar fecha de actualización
            update_dict['fecha_actualizacion'] = datetime.utcnow()
            
            # Si se actualiza el paciente, agregar fecha de actualización del paciente
            if 'paciente' in update_dict and update_dict['paciente']:
                if isinstance(update_dict['paciente'], dict):
                    update_dict['paciente']['fecha_actualizacion'] = datetime.utcnow()
            
            # Si se actualiza el estado a "Completado", agregar fecha de entrega
            if update_dict.get("estado") == "Completado" and not update_dict.get("fecha_entrega"):
                update_dict["fecha_entrega"] = datetime.utcnow()
            
            # Si se actualiza el estado a "Por firmar", agregar fecha de firma
            if update_dict.get("estado") == "Por firmar" and not update_dict.get("fecha_firma"):
                update_dict["fecha_firma"] = datetime.utcnow()
            
            # Actualizar en la base de datos
            result = await self.collection.find_one_and_update(
                {"caso_code": caso_code},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                # Convertir ObjectId a string
                result['_id'] = str(result['_id'])
                return result
            
            return None
            
        except Exception as e:
            raise Exception(f"Error actualizando caso {caso_code}: {str(e)}")
    
    async def get_case_by_code(self, caso_code: str) -> Optional[Dict[str, Any]]:
        """Obtener un caso por código"""
        try:
            case = await self.collection.find_one({"caso_code": caso_code})
            if case:
                case['_id'] = str(case['_id'])
            return case
        except Exception as e:
            raise Exception(f"Error obteniendo caso {caso_code}: {str(e)}")
    
    async def validate_case_exists(self, caso_code: str) -> bool:
        """Validar que el caso existe"""
        try:
            count = await self.collection.count_documents({"caso_code": caso_code})
            return count > 0
        except Exception as e:
            raise Exception(f"Error validando existencia del caso {caso_code}: {str(e)}")
    
