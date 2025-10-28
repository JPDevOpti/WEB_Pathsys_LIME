from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import TEXT
from ..schemas import PatientCreate, PatientUpdate, PatientSearch
from app.core.exceptions import ConflictError, NotFoundError
import logging

logger = logging.getLogger(__name__)

class PatientRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.patients
        # Ensure indexes for better performance (execute asynchronously)
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._ensure_indexes())
        except RuntimeError:
            # If there's no running loop (e.g., during app startup tests), skip silently
            pass

    async def ensure_indexes(self):
        """Public wrapper to initialize indexes at application startup."""
        await self._ensure_indexes()

    async def _ensure_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Unique index for patient_code
            await self.collection.create_index("patient_code", unique=True)
            
            # Compound index for identification
            await self.collection.create_index([
                ("identification_type", 1),
                ("identification_number", 1)
            ], unique=True)
            
            # Text index for search functionality
            await self.collection.create_index([
                ("first_name", TEXT),
                ("first_lastname", TEXT),
                ("second_name", TEXT),
                ("second_lastname", TEXT)
            ], name="patient_text_search", default_language="spanish", weights={
                "first_name": 10,
                "first_lastname": 10,
                "second_name": 5,
                "second_lastname": 5
            })
            
            # Indexes for common filters
            await self.collection.create_index("gender")
            await self.collection.create_index("care_type")
            await self.collection.create_index("birth_date")
            await self.collection.create_index("created_at")
            await self.collection.create_index("entity_info.name")
            await self.collection.create_index("location.municipality_code")
            
        except Exception:
            # Indexes might already exist, continue silently
            pass
    
    def _prepare_data_for_mongo(self, data: dict) -> dict:
        prepared_data = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                prepared_data[key] = value
            elif isinstance(value, date):
                prepared_data[key] = datetime.combine(value, datetime.min.time())
            else:
                prepared_data[key] = value
        return prepared_data

    def _convert_doc_to_response(self, doc: dict) -> dict:
        if doc:
            doc["id"] = str(doc["_id"])
            # Convert datetime back to date for birth_date
            if "birth_date" in doc and isinstance(doc["birth_date"], datetime):
                doc["birth_date"] = doc["birth_date"].date()
        return doc

    async def create(self, patient: PatientCreate) -> dict:
        try:
            if not patient.patient_code:
                patient.patient_code = f"{patient.identification_type}-{patient.identification_number}"
            logger.info("[repo:create] Generado patient_code=%s", patient.patient_code)
            
            # Check for existing patient using index
            existing_patient = await self.collection.find_one(
                {"patient_code": patient.patient_code},
                {"_id": 1}  # Only return _id for existence check
            )
            if existing_patient:
                raise ConflictError(f"Ya existe un paciente con el código {patient.patient_code}")
            
            patient_data = patient.model_dump()
            logger.debug("[repo:create] Datos del paciente a insertar: %s", {k: patient_data.get(k) for k in ["patient_code","identification_type","identification_number","first_name","first_lastname","birth_date","gender","entity_info","location"]})
            patient_data["created_at"] = datetime.now(timezone.utc)
            patient_data["updated_at"] = datetime.now(timezone.utc)
            
            mongo_data = self._prepare_data_for_mongo(patient_data)
            
            result = await self.collection.insert_one(mongo_data)
            created_patient = await self.collection.find_one({"_id": result.inserted_id})
            if not created_patient:
                raise ConflictError("Error al crear el paciente")
            return self._convert_doc_to_response(dict(created_patient))
        except DuplicateKeyError:
            logger.exception("[repo:create] Duplicated key al crear paciente")
            raise ConflictError("Error al crear el paciente: datos duplicados")

    async def get_by_id(self, patient_code: str) -> Optional[dict]:
        patient = await self.collection.find_one({"patient_code": patient_code})
        return self._convert_doc_to_response(dict(patient)) if patient else None

    async def update(self, patient_code: str, patient_update: PatientUpdate) -> dict:
        query = {"patient_code": patient_code}
            
        # Check existence first
        existing_patient = await self.collection.find_one(query, {"_id": 1})
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")
            
        update_data = patient_update.model_dump(exclude_none=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            mongo_data = self._prepare_data_for_mongo(update_data)
            await self.collection.update_one(query, {"$set": mongo_data})
            
        updated_patient = await self.collection.find_one(query)
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después de la actualización")
        return self._convert_doc_to_response(dict(updated_patient))

    async def change_identification(self, old_code: str, new_identification_type: str, new_identification_number: str, cases_collection) -> dict:
        old_query = {"patient_code": old_code}
            
        existing_patient = await self.collection.find_one(old_query, {"_id": 1})
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")
            
        new_code = f"{new_identification_type}-{new_identification_number}"
        duplicated = await self.collection.find_one({"patient_code": new_code}, {"_id": 1})
        if duplicated:
            raise ConflictError(f"Ya existe un paciente con {new_identification_type}: {new_identification_number}")
            
        await self.collection.update_one(
            old_query,
            {"$set": {
                "identification_type": new_identification_type,
                "identification_number": new_identification_number,
                "patient_code": new_code,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        if cases_collection is not None:
            await cases_collection.update_many(
                {"patient_info.patient_code": old_code},
                {"$set": {"patient_info.patient_code": new_code}}
            )
            
        updated_patient = await self.collection.find_one({"patient_code": new_code})
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después del cambio de identificación")
        return self._convert_doc_to_response(dict(updated_patient))

    async def delete(self, patient_code: str) -> bool:
        query = {"patient_code": patient_code}
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

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
            # Check if search term is numeric (identification number)
            if search.isdigit():
                # Search by identification number
                filter_dict["identification_number"] = {"$regex": f"^{search}", "$options": "i"}
            else:
                # Use multiple field search for text
                filter_dict["$or"] = [
                    {"first_name": {"$regex": search, "$options": "i"}},
                    {"first_lastname": {"$regex": search, "$options": "i"}},
                    {"second_name": {"$regex": search, "$options": "i"}},
                    {"second_lastname": {"$regex": search, "$options": "i"}},
                    {"identification_number": {"$regex": search, "$options": "i"}},
                    {"patient_code": {"$regex": search, "$options": "i"}}
                ]
        
        if entity:
            filter_dict["entity_info.name"] = {"$regex": entity, "$options": "i"}
        if gender:
            filter_dict["gender"] = gender
        if care_type:
            filter_dict["care_type"] = care_type
            
        # Use projection to limit returned fields if needed
        cursor = self.collection.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
        patients = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(p) for p in patients]

    async def advanced_search(self, search_params: PatientSearch) -> Dict[str, Any]:
        filter_dict = {}
        
        # Use exact match for indexed fields
        if search_params.identification_type:
            filter_dict["identification_type"] = search_params.identification_type
        if search_params.identification_number:
            filter_dict["identification_number"] = {"$regex": f"^{search_params.identification_number}", "$options": "i"}
            
        if search_params.first_name:
            filter_dict["first_name"] = {"$regex": f"^{search_params.first_name}", "$options": "i"}
        if search_params.first_lastname:
            filter_dict["first_lastname"] = {"$regex": f"^{search_params.first_lastname}", "$options": "i"}
            
        # Optimize date range queries
        if search_params.birth_date_from or search_params.birth_date_to:
            birth_date_filter = {}
            if search_params.birth_date_from:
                birth_date_filter["$gte"] = datetime.combine(search_params.birth_date_from, datetime.min.time())
            if search_params.birth_date_to:
                birth_date_filter["$lte"] = datetime.combine(search_params.birth_date_to, datetime.max.time())
            filter_dict["birth_date"] = birth_date_filter
            
        if search_params.municipality_code:
            filter_dict["location.municipality_code"] = search_params.municipality_code
        if search_params.municipality_name:
            filter_dict["location.municipality_name"] = {"$regex": f"^{search_params.municipality_name}", "$options": "i"}
        if search_params.subregion:
            filter_dict["location.subregion"] = {"$regex": f"^{search_params.subregion}", "$options": "i"}
            
        # Optimize age-based queries
        if search_params.age_min is not None or search_params.age_max is not None:
            today = date.today()
            age_filter = {}
            if search_params.age_max is not None:
                min_birth_date = datetime.combine(
                    date(today.year - search_params.age_max - 1, today.month, today.day),
                    datetime.min.time()
                )
                age_filter["$gte"] = min_birth_date
            if search_params.age_min is not None:
                max_birth_date = datetime.combine(
                    date(today.year - search_params.age_min, today.month, today.day),
                    datetime.max.time()
                )
                age_filter["$lte"] = max_birth_date
            
            if "birth_date" in filter_dict:
                # Merge with existing birth_date filter
                filter_dict["birth_date"].update(age_filter)
            else:
                filter_dict["birth_date"] = age_filter
                
        if hasattr(search_params, 'entity') and search_params.entity:
            filter_dict["entity_info.name"] = {"$regex": f"^{search_params.entity}", "$options": "i"}
        if search_params.gender:
            filter_dict["gender"] = search_params.gender
        if search_params.care_type:
            filter_dict["care_type"] = search_params.care_type
            
        if search_params.date_from or search_params.date_to:
            date_filter = {}
            if search_params.date_from:
                date_filter["$gte"] = datetime.fromisoformat(search_params.date_from)
            if search_params.date_to:
                date_filter["$lte"] = datetime.fromisoformat(search_params.date_to + "T23:59:59")
            filter_dict["created_at"] = date_filter
            
        # Use aggregation for better performance with large datasets
        pipeline = [
            {"$match": filter_dict},
            {"$facet": {
                "patients": [
                    {"$sort": {"created_at": -1}},
                    {"$skip": search_params.skip},
                    {"$limit": search_params.limit}
                ],
                "total": [{"$count": "count"}]
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            patients = result[0]["patients"]
            total = result[0]["total"][0]["count"] if result[0]["total"] else 0
        else:
            patients = []
            total = 0
            
        return {
            "patients": [self._convert_doc_to_response(p) for p in patients],
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit
        }

    async def count_total(self) -> int:
        return await self.collection.estimated_document_count()

    # Método 'exists' eliminado: usar get_by_id en el servicio para verificar existencia
