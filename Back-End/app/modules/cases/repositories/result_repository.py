from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class ResultRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cases

    async def update_result(self, case_code: str, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar resultado de un caso"""
        now = datetime.utcnow()
        
        # Preparar los datos del resultado
        result_update = {
            "result": {
                **result_data,
                "updated_at": now
            },
            "updated_at": now
        }
        
        # Actualizar el documento
        await self.collection.update_one(
            {"case_code": case_code},
            {"$set": result_update}
        )
        
        # Retornar el documento actualizado
        return await self.collection.find_one({"case_code": case_code})

    async def get_result(self, case_code: str) -> Optional[Dict[str, Any]]:
        """Obtener resultado de un caso"""
        doc = await self.collection.find_one(
            {"case_code": case_code},
            {"result": 1, "state": 1, "case_code": 1}
        )
        return doc

    async def validate_case_not_completed(self, case_code: str) -> bool:
        """Validar que el caso no esté completado"""
        doc = await self.collection.find_one(
            {"case_code": case_code},
            {"state": 1}
        )
        
        if not doc:
            return False
            
        # Estados que permiten edición
        editable_states = ["En proceso", "Por firmar"]
        return doc.get("state") in editable_states

    async def get_case_state(self, case_code: str) -> Optional[str]:
        """Obtener el estado actual del caso"""
        doc = await self.collection.find_one(
            {"case_code": case_code},
            {"state": 1}
        )
        return doc.get("state") if doc else None
