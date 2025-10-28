from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class ResultRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cases

    async def update_result(self, case_code: str, result_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        doc = await self.collection.find_one({"case_code": case_code})
        result = {**(doc.get("result", {}) if doc else {}), **result_data, "updated_at": now}
        await self.collection.update_one({"case_code": case_code}, {"$set": {"result": result, "updated_at": now}})
        return await self.collection.find_one({"case_code": case_code})

    async def get_result(self, case_code: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"case_code": case_code}, {"result": 1, "state": 1, "case_code": 1})

    async def validate_case_not_completed(self, case_code: str) -> bool:
        doc = await self.collection.find_one({"case_code": case_code}, {"state": 1})
        return bool(doc) and doc.get("state") in ["En proceso", "Por firmar"]

    async def get_case_state(self, case_code: str) -> Optional[str]:
        doc = await self.collection.find_one({"case_code": case_code}, {"state": 1})
        return doc.get("state") if doc else None
