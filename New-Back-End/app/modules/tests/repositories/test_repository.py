from typing import List, Optional, Dict
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import TestCreate, TestUpdate, TestSearch

class TestRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.tests

    def _convert(self, doc: dict) -> dict:
        if doc:
            doc["id"] = str(doc.get("_id"))
        return doc

    async def create(self, data: TestCreate) -> dict:
        doc = data.dict()
        doc["created_at"] = datetime.now(timezone.utc)
        doc["updated_at"] = datetime.now(timezone.utc)
        await self.collection.insert_one(doc)
        created = await self.collection.find_one({"test_code": data.test_code})
        return self._convert(dict(created)) if created else None

    async def get_by_code(self, code: str) -> Optional[dict]:
        found = await self.collection.find_one({"test_code": code.upper()})
        return self._convert(dict(found)) if found else None

    async def list_active(self, search: TestSearch) -> List[dict]:
        f: Dict = {"is_active": True}
        if search.query:
            f["$or"] = [
                {"name": {"$regex": search.query, "$options": "i"}},
                {"test_code": {"$regex": search.query, "$options": "i"}},
                {"description": {"$regex": search.query, "$options": "i"}},
            ]
        cursor = self.collection.find(f).skip(search.skip).limit(search.limit).sort("created_at", -1)
        docs = await cursor.to_list(length=search.limit)
        return [self._convert(d) for d in docs]

    async def list_all(self, search: TestSearch) -> List[dict]:
        f: Dict = {}
        if search.query:
            f["$or"] = [
                {"name": {"$regex": search.query, "$options": "i"}},
                {"test_code": {"$regex": search.query, "$options": "i"}},
                {"description": {"$regex": search.query, "$options": "i"}},
            ]
        cursor = self.collection.find(f).skip(search.skip).limit(search.limit).sort("created_at", -1)
        docs = await cursor.to_list(length=search.limit)
        return [self._convert(d) for d in docs]

    async def update_by_code(self, code: str, update: TestUpdate) -> Optional[dict]:
        existing = await self.collection.find_one({"test_code": code.upper()})
        if not existing:
            return None
        upd = {k: v for k, v in update.dict().items() if v is not None}
        if not upd:
            return self._convert(dict(existing))
        upd["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"test_code": code.upper()}, {"$set": upd})
        new_code = (upd.get("test_code") or code).upper()
        updated = await self.collection.find_one({"test_code": new_code})
        return self._convert(dict(updated)) if updated else None

    async def delete_by_code(self, code: str) -> bool:
        res = await self.collection.delete_one({"test_code": code.upper()})
        return res.deleted_count > 0

    async def exists_code(self, code: str) -> bool:
        return await self.collection.count_documents({"test_code": code.upper()}) > 0
