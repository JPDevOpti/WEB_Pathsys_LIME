from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from ..schemas import PatientCreate, PatientUpdate, PatientSearch
from app.core.exceptions import ConflictError, NotFoundError

class PatientRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.patients

    def _convert_doc_to_response(self, doc: dict) -> dict:
        if doc:
            doc["id"] = str(doc["_id"])
            doc["patient_code"] = doc.get("patient_code", "")
        return doc

    async def create(self, patient: PatientCreate) -> dict:
        try:
            patient_data = patient.dict()
            patient_data["created_at"] = datetime.now(timezone.utc)
            patient_data["updated_at"] = datetime.now(timezone.utc)
            await self.collection.insert_one(patient_data)
            created_patient = await self.collection.find_one({"patient_code": patient.patient_code})
            if not created_patient:
                raise ConflictError("Error creating patient")
            return self._convert_doc_to_response(dict(created_patient))
        except DuplicateKeyError:
            raise ConflictError(f"Patient with code {patient.patient_code} already exists")

    async def get_by_id(self, patient_code: str) -> Optional[dict]:
        patient = await self.collection.find_one({"patient_code": patient_code})
        return self._convert_doc_to_response(dict(patient)) if patient else None

    async def update(self, patient_code: str, patient_update: PatientUpdate) -> dict:
        existing_patient = await self.collection.find_one({"patient_code": patient_code})
        if not existing_patient:
            raise NotFoundError("Patient not found")
        update_data = {k: v for k, v in patient_update.dict().items() if v is not None}
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await self.collection.update_one({"patient_code": patient_code}, {"$set": update_data})
        updated_patient = await self.collection.find_one({"patient_code": patient_code})
        if not updated_patient:
            raise NotFoundError("Patient not found after update")
        return self._convert_doc_to_response(dict(updated_patient))

    async def change_code(self, old_code: str, new_code: str, cases_collection) -> dict:
        existing_patient = await self.collection.find_one({"patient_code": old_code})
        if not existing_patient:
            raise NotFoundError("Patient not found")
        duplicated = await self.collection.find_one({"patient_code": new_code})
        if duplicated:
            raise ConflictError(f"Patient with code {new_code} already exists")
        await self.collection.update_one(
            {"patient_code": old_code},
            {"$set": {"patient_code": new_code, "updated_at": datetime.now(timezone.utc)}}
        )
        if cases_collection is not None:
            await cases_collection.update_many(
                {"patient.patient_code": old_code},
                {"$set": {"patient.patient_code": new_code}}
            )
        updated_patient = await self.collection.find_one({"patient_code": new_code})
        if not updated_patient:
            raise NotFoundError("Patient not found after code change")
        return self._convert_doc_to_response(dict(updated_patient))

    async def delete(self, patient_code: str) -> bool:
        result = await self.collection.delete_one({"patient_code": patient_code})
        if result.deleted_count == 0:
            raise NotFoundError("Patient not found")
        return True

    async def list_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        entity: Optional[str] = None,
        gender: Optional[str] = None,
        care_type: Optional[str] = None
    ) -> List[dict]:
        filter_dict = {}
        if search:
            filter_dict["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"patient_code": {"$regex": str(search), "$options": "i"}}
            ]
        if entity:
            filter_dict["entity_info.name"] = {"$regex": entity, "$options": "i"}
        if gender:
            filter_dict["gender"] = gender
        if care_type:
            filter_dict["care_type"] = care_type
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
        patients = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(p) for p in patients]

    async def advanced_search(self, search_params: PatientSearch) -> Dict[str, Any]:
        filter_dict = {}
        if search_params.name:
            filter_dict["name"] = {"$regex": search_params.name, "$options": "i"}
        if search_params.patient_code:
            filter_dict["patient_code"] = {"$regex": search_params.patient_code, "$options": "i"}
        if search_params.age_min is not None or search_params.age_max is not None:
            age_filter = {}
            if search_params.age_min is not None:
                age_filter["$gte"] = search_params.age_min
            if search_params.age_max is not None:
                age_filter["$lte"] = search_params.age_max
            filter_dict["age"] = age_filter
        if hasattr(search_params, 'entity') and search_params.entity:
            filter_dict["entity_info.name"] = {"$regex": search_params.entity, "$options": "i"}
        if search_params.gender:
            filter_dict["gender"] = search_params.gender.value
        if search_params.care_type:
            filter_dict["care_type"] = search_params.care_type.value
        if search_params.date_from or search_params.date_to:
            date_filter = {}
            if search_params.date_from:
                date_filter["$gte"] = datetime.fromisoformat(search_params.date_from)
            if search_params.date_to:
                date_filter["$lte"] = datetime.fromisoformat(search_params.date_to + "T23:59:59")
            filter_dict["created_at"] = date_filter
        total = await self.collection.count_documents(filter_dict)
        cursor = self.collection.find(filter_dict).skip(search_params.skip).limit(search_params.limit).sort("created_at", -1)
        patients = await cursor.to_list(length=search_params.limit)
        return {
            "patients": [self._convert_doc_to_response(p) for p in patients],
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit
        }

    async def count_total(self) -> int:
        return await self.collection.count_documents({})

    async def exists(self, patient_code: str) -> bool:
        count = await self.collection.count_documents({"patient_code": patient_code})
        return count > 0
