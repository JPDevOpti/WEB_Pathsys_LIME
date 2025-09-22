from typing import List, Optional, Dict
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import EntityCreate, EntityUpdate, EntitySearch

class EntityRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.entities

    def _convert(self, doc: dict) -> dict:
        if doc:
            doc["id"] = str(doc.get("_id"))
        return doc

    async def create(self, data: EntityCreate) -> dict:
        entity = data.dict()
        entity["created_at"] = datetime.now(timezone.utc)
        entity["updated_at"] = datetime.now(timezone.utc)
        await self.collection.insert_one(entity)
        # Compat: persist under entity_code; read legacy 'code' if present
        created = await self.collection.find_one({"entity_code": data.entity_code}) or await self.collection.find_one({"code": data.entity_code})
        return self._convert(dict(created)) if created else None

    async def get_by_code(self, code: str) -> Optional[dict]:
        found = await self.collection.find_one({"entity_code": code.upper()}) or await self.collection.find_one({"code": code.upper()})
        return self._convert(dict(found)) if found else None

    async def list_active(self, search: EntitySearch) -> List[dict]:
        f: Dict = {"is_active": True}
        if search.query:
            f["$or"] = [
                {"name": {"$regex": search.query, "$options": "i"}},
                {"entity_code": {"$regex": search.query, "$options": "i"}},
                {"notes": {"$regex": search.query, "$options": "i"}},
            ]
        cursor = self.collection.find(f).skip(search.skip).limit(search.limit).sort("created_at", -1)
        docs = await cursor.to_list(length=search.limit)
        return [self._convert(d) for d in docs]

    async def list_all(self, search: EntitySearch) -> List[dict]:
        f: Dict = {}
        if search.query:
            f["$or"] = [
                {"name": {"$regex": search.query, "$options": "i"}},
                {"entity_code": {"$regex": search.query, "$options": "i"}},
                {"notes": {"$regex": search.query, "$options": "i"}},
            ]
        cursor = self.collection.find(f).skip(search.skip).limit(search.limit).sort("created_at", -1)
        docs = await cursor.to_list(length=search.limit)
        return [self._convert(d) for d in docs]

    async def update_by_code(self, code: str, update: EntityUpdate) -> Optional[dict]:
        existing = await self.collection.find_one({"entity_code": code.upper()}) or await self.collection.find_one({"code": code.upper()})
        if not existing:
            return None
        upd = {k: v for k, v in update.dict().items() if v is not None}
        if not upd:
            return self._convert(dict(existing))
        upd["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"entity_code": code.upper()}, {"$set": upd})
        updated_code = (upd.get("entity_code") or code).upper()
        updated = await self.collection.find_one({"entity_code": updated_code}) or await self.collection.find_one({"code": updated_code})
        return self._convert(dict(updated)) if updated else None

    async def delete_by_code(self, code: str) -> bool:
        res = await self.collection.delete_one({"entity_code": code.upper()})
        return res.deleted_count > 0

    async def exists_code(self, code: str) -> bool:
        return (await self.collection.count_documents({"entity_code": code.upper()}) > 0) or (await self.collection.count_documents({"code": code.upper()}) > 0)
