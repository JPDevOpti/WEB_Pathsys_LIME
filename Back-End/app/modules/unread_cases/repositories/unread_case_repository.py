"""Mongo repository for unread cases."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.unread_case import UnreadCaseCreate, UnreadCaseFilter, UnreadCaseUpdate


class UnreadCaseRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database.unread_cases
        self.counter_collection = database.unread_cases_counters

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("case_code", unique=True)
        await self.collection.create_index("entry_date")
        await self.collection.create_index("status")
        await self.collection.create_index("entity_code")
        await self.collection.create_index("patient_document")

    async def _get_next_sequence(self, prefix: str) -> int:
        doc = await self.counter_collection.find_one_and_update(
            {"_id": prefix},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True,
        )
        return doc["seq"] if doc and "seq" in doc else 1

    async def generate_case_code(self) -> str:
        current_year = datetime.now().year
        prefix = f"{current_year}"
        sequence = await self._get_next_sequence(prefix)
        return f"TC{current_year}-{sequence:05d}"

    @staticmethod
    def _convert(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        data = dict(doc)
        data["id"] = str(data.pop("_id")) if "_id" in data else data.get("id")
        return data

    async def create(self, data: UnreadCaseCreate, case_code: str) -> Dict[str, Any]:
        payload = data.dict(by_alias=False)
        payload["case_code"] = case_code
        payload["institution"] = payload.get("institution") or payload.get("entity_name") or ""
        payload["number_of_plates"] = payload.get("number_of_plates") or 0
        payload["delivered_to"] = payload.get("delivered_to") or ""
        payload["delivery_date"] = payload.get("delivery_date") or ""
        payload["status"] = payload.get("status") or "En proceso"
        payload["elaborated_by"] = payload.get("elaborated_by") or ""
        payload["receipt"] = payload.get("receipt") or ""
        now = datetime.now(timezone.utc)
        payload["created_at"] = now
        payload["updated_at"] = now
        await self.collection.insert_one(payload)
        created = await self.collection.find_one({"case_code": case_code})
        return self._convert(created) or {}

    async def get_by_case_code(self, case_code: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"case_code": case_code.upper()})
        return self._convert(doc)

    async def exists_case_code(self, case_code: str) -> bool:
        return await self.collection.count_documents({"case_code": case_code.upper()}, limit=1) > 0

    async def update_by_case_code(self, case_code: str, update: UnreadCaseUpdate) -> Optional[Dict[str, Any]]:
        existing = await self.collection.find_one({"case_code": case_code.upper()})
        if not existing:
            return None

        update_data = {k: v for k, v in update.dict(by_alias=False).items() if v is not None}
        if not update_data:
            return self._convert(existing)

        if "entity_name" in update_data and "institution" not in update_data:
            update_data["institution"] = update_data.get("entity_name")
        if "number_of_plates" in update_data and update_data["number_of_plates"] is None:
            update_data.pop("number_of_plates")

        update_data["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"case_code": case_code.upper()}, {"$set": update_data})
        updated = await self.collection.find_one({"case_code": case_code.upper()})
        return self._convert(updated)

    async def list(self, filters: UnreadCaseFilter) -> Tuple[List[Dict[str, Any]], int]:
        query: Dict[str, Any] = {}

        if filters.search_query:
            pattern = {"$regex": filters.search_query, "$options": "i"}
            query["$or"] = [
                {"case_code": pattern},
                {"patient_document": pattern},
                {"patient_name": pattern},
            ]

        if filters.selected_institution:
            query["institution"] = {"$regex": filters.selected_institution, "$options": "i"}

        if filters.selected_test_type:
            test_type_map = {
                "low_complexity": "LOW_COMPLEXITY_IHQ",
                "high_complexity": "HIGH_COMPLEXITY_IHQ",
                "special": "SPECIAL_IHQ",
                "histochemistry": "HISTOCHEMISTRY",
            }
            mapped_type = test_type_map.get(filters.selected_test_type, filters.selected_test_type.upper())
            query["test_groups.type"] = mapped_type

        if filters.selected_status:
            query["status"] = filters.selected_status

        if filters.date_from or filters.date_to:
            range_query: Dict[str, Any] = {}
            if filters.date_from:
                range_query["$gte"] = filters.date_from
            if filters.date_to:
                range_query["$lte"] = filters.date_to
            query["entry_date"] = range_query

        sort_field_map = {
            "caseCode": "case_code",
            "patientName": "patient_name",
            "patientDocument": "patient_document",
            "institution": "institution",
            "numberOfPlates": "number_of_plates",
            "deliveredTo": "delivered_to",
            "deliveryDate": "delivery_date",
            "status": "status",
            "entryDate": "entry_date",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }

        sort_field = sort_field_map.get(filters.sort_key or "entryDate", filters.sort_key or "entry_date")
        if sort_field not in {"case_code", "entry_date", "status", "number_of_plates", "delivery_date", "created_at", "updated_at", "institution"}:
            sort_field = "entry_date"

        sort_order = -1 if (filters.sort_order or "desc").lower() == "desc" else 1

        skip = (filters.page - 1) * filters.limit

        cursor = (
            self.collection
            .find(query)
            .skip(skip)
            .limit(filters.limit)
            .sort(sort_field, sort_order)
        )
        docs = await cursor.to_list(length=filters.limit)
        total = await self.collection.count_documents(query)
        return [self._convert(doc) for doc in docs if doc], total

    async def mark_delivered(self, case_codes: List[str], delivered_to: str, delivery_date: Optional[str]) -> List[Dict[str, Any]]:
        if not case_codes:
            return []

        payload: Dict[str, Any] = {
            "delivered_to": delivered_to,
            "status": "Completado",
            "updated_at": datetime.now(timezone.utc),
        }
        if delivery_date:
            payload["delivery_date"] = delivery_date
        else:
            payload["delivery_date"] = datetime.now(timezone.utc).isoformat()

        await self.collection.update_many(
            {"case_code": {"$in": [code.upper() for code in case_codes]}},
            {"$set": payload},
        )

        cursor = self.collection.find({"case_code": {"$in": [code.upper() for code in case_codes]}})
        docs = await cursor.to_list(length=len(case_codes))
        return [self._convert(doc) for doc in docs if doc]

