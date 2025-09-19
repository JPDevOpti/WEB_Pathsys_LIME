from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class CaseRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cases

    async def ensure_indexes(self):
        await self.collection.create_index("case_code", unique=True)
        await self.collection.create_index("patient_info.patient_code")
        await self.collection.create_index("state")
        await self.collection.create_index("created_at")
        await self.collection.create_index("assigned_pathologist.name")
        await self.collection.create_index("patient_info.entity_info.name")
        await self.collection.create_index("samples.tests.id")
        # Índice compuesto para búsquedas comunes
        await self.collection.create_index([
            ("created_at", -1),
            ("state", 1),
            ("assigned_pathologist.name", 1)
        ])

    async def get_by_case_code(self, case_code: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"case_code": case_code})

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.utcnow()
        data.setdefault("created_at", now)
        data["updated_at"] = now
        res = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": res.inserted_id})

    async def update_by_case_code(self, case_code: str, update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update["updated_at"] = datetime.utcnow()
        await self.collection.update_one({"case_code": case_code}, {"$set": update})
        return await self.get_by_case_code(case_code)

    async def delete_by_case_code(self, case_code: str) -> bool:
        res = await self.collection.delete_one({"case_code": case_code})
        return res.deleted_count > 0


