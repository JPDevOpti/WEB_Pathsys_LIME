from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class SignRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cases

    async def sign_case(self, case_code: str, sign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Firmar un caso cambiando su estado de 'Por firmar' a 'Por entregar'"""
        now = datetime.utcnow()
        
        # Preparar datos de firma a nivel de caso
        case_update = {
            "state": "Por entregar",
            "signed_at": now,
            "updated_at": now
        }
        
        # Preparar datos del resultado
        result_data = {
            "method": sign_data.get("method"),
            "macro_result": sign_data.get("macro_result"),
            "micro_result": sign_data.get("micro_result"),
            "diagnosis": sign_data.get("diagnosis"),
            "observations": sign_data.get("observations"),
            "cie10_diagnosis": sign_data.get("cie10_diagnosis"),
            "cieo_diagnosis": sign_data.get("cieo_diagnosis"),
            "updated_at": now
        }
        
        # Filtrar campos None para evitar sobrescribir con valores nulos
        filtered_result_data = {k: v for k, v in result_data.items() if v is not None}
        
        # Actualizar el documento
        await self.collection.update_one(
            {"case_code": case_code},
            {
                "$set": {
                    **case_update,
                    "result": filtered_result_data
                }
            }
        )
        
        # Retornar el documento actualizado
        return await self.collection.find_one({"case_code": case_code})

    async def validate_case_can_be_signed(self, case_code: str) -> bool:
        """Validar que el caso puede ser firmado"""
        doc = await self.collection.find_one(
            {"case_code": case_code},
            {"state": 1, "assigned_pathologist": 1}
        )
        
        if not doc:
            return False
            
        # Se pueden firmar todos los casos excepto los completados
        state = doc.get("state")
        if state == "Completado":
            return False
            
        # El caso debe tener un patólogo asignado para poder ser firmado
        assigned_pathologist = doc.get("assigned_pathologist")
        if not assigned_pathologist or not assigned_pathologist.get("name"):
            return False
            
        return True

    async def get_case_for_signing(self, case_code: str) -> Optional[Dict[str, Any]]:
        """Obtener caso para validaciones de firma"""
        return await self.collection.find_one(
            {"case_code": case_code},
            {"state": 1, "assigned_pathologist": 1, "case_code": 1}
        )

    async def get_case_state(self, case_code: str) -> Optional[str]:
        """Obtener el estado actual del caso"""
        doc = await self.collection.find_one(
            {"case_code": case_code},
            {"state": 1}
        )
        return doc.get("state") if doc else None
