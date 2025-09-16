from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr
from bson import ObjectId


class AuthRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db.get_collection("usuarios")

    async def get_user_by_email(self, email: EmailStr) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"email": email, "is_active": True})
        if not doc:
            return None
        doc["_id"] = str(doc.get("_id", ""))
        return doc

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        doc = await self.collection.find_one({"_id": oid, "is_active": True})
        if not doc:
            return None
        doc["_id"] = str(doc.get("_id", ""))
        return doc


