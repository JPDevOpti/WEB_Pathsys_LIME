from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


class SignRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cases

    async def sign_case(self, case_code: str, sign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        result = {k: v for k, v in {
            "method": sign_data.get("method"),
            "macro_result": sign_data.get("macro_result"),
            "micro_result": sign_data.get("micro_result"),
            "diagnosis": sign_data.get("diagnosis"),
            "observations": sign_data.get("observations"),
            "cie10_diagnosis": sign_data.get("cie10_diagnosis"),
            "cieo_diagnosis": sign_data.get("cieo_diagnosis"),
            "updated_at": now
        }.items() if v is not None}
        await self.collection.update_one(
            {"case_code": case_code},
            {"$set": {"state": "Por entregar", "signed_at": now, "updated_at": now, "result": result}}
        )
        return await self.collection.find_one({"case_code": case_code})

    async def validate_case_can_be_signed(self, case_code: str) -> bool:
        doc = await self.collection.find_one({"case_code": case_code}, {"state": 1, "assigned_pathologist": 1})
        if not doc or doc.get("state") == "Completado":
            return False
        ap = doc.get("assigned_pathologist")
        return bool(ap and ap.get("name"))

    async def get_case_for_signing(self, case_code: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"case_code": case_code}, {"state": 1, "assigned_pathologist": 1, "case_code": 1})

    async def get_case_state(self, case_code: str) -> Optional[str]:
        doc = await self.collection.find_one({"case_code": case_code}, {"state": 1})
        return doc.get("state") if doc else None
