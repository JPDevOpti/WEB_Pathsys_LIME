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
            
        # Incluir solo campos explícitamente enviados, incluso si son None (para poder hacer unset)
        update_data = patient_update.model_dump(exclude_unset=True)
        if update_data:
            # Construir operaciones $set y $unset, manejando correctamente nested fields (location)
            set_ops: Dict[str, Any] = {}
            # Valores de $unset pueden ser "" o 1; tipamos como Any para evitar errores de tipo
            unset_ops: Dict[str, Any] = {}

            # updated_at siempre se setea
            set_ops["updated_at"] = datetime.now(timezone.utc)

            for key, value in update_data.items():
                if key == "location":
                    # Si location viene como None, eliminar todo el objeto
                    if value is None:
                        unset_ops["location"] = ""
                    elif isinstance(value, dict):
                        # Actualizar campos anidados individualmente
                        for loc_key, loc_value in value.items():
                            field_path = f"location.{loc_key}"
                            if loc_value is None:
                                unset_ops[field_path] = ""
                            else:
                                set_ops[field_path] = loc_value
                    # Si viene en un tipo inesperado, lo ignoramos para evitar corrupción
                else:
                    if value is None:
                        unset_ops[key] = ""
                    else:
                        set_ops[key] = value

            # Preparar solo los valores de $set para Mongo (p.ej. fechas)
            if set_ops:
                set_ops = self._prepare_data_for_mongo(set_ops)

            update_ops: Dict[str, Any] = {}
            if set_ops:
                update_ops["$set"] = set_ops
            if unset_ops:
                update_ops["$unset"] = unset_ops

            if update_ops:
                await self.collection.update_one(query, update_ops)
            
        updated_patient = await self.collection.find_one(query)
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después de la actualización")
        return self._convert_doc_to_response(dict(updated_patient))

    async def change_identification(self, old_code: str, new_identification_type: str, new_identification_number: str, cases_collection) -> dict:
        old_query = {"patient_code": old_code}

        # Obtener el paciente actual (doc completo para poder comparar y potencialmente devolverlo)
        existing_patient = await self.collection.find_one(old_query)
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")

        new_code = f"{new_identification_type}-{new_identification_number}"

        # Si el nuevo código es igual al actual, no hacer cambios y devolver el paciente tal cual
        if new_code == old_code:
            return self._convert_doc_to_response(dict(existing_patient))

        # Verificar duplicados excluyendo al mismo paciente
        duplicated = await self.collection.find_one({"patient_code": new_code}, {"_id": 1})
        if duplicated and duplicated.get("_id") != existing_patient.get("_id"):
            raise ConflictError(f"Ya existe un paciente con {new_identification_type}: {new_identification_number}")

        # Actualizar identificación y patient_code
        await self.collection.update_one(
            old_query,
            {"$set": {
                "identification_type": new_identification_type,
                "identification_number": new_identification_number,
                "patient_code": new_code,
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        # Propagar el nuevo código a casos asociados, si corresponde
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

    async def search(self, search_params: PatientSearch) -> Dict[str, Any]:
        filter_dict = {
            "patient_code": {"$exists": True, "$ne": None},
            "identification_type": {"$exists": True, "$ne": None},
            "identification_number": {"$exists": True, "$ne": None},
            "first_name": {"$exists": True, "$ne": None},
            "first_lastname": {"$exists": True, "$ne": None},
            "birth_date": {"$exists": True, "$ne": None},
            "gender": {"$exists": True, "$ne": None},
            "entity_info": {"$exists": True, "$ne": None},
            "care_type": {"$exists": True, "$ne": None}
        }
        
        if search_params.identification_type:
            filter_dict["identification_type"] = search_params.identification_type
        
        if search_params.identification_number:
            if search_params.identification_type is not None:
                filter_dict["identification_number"] = search_params.identification_number
            else:
                filter_dict["identification_number"] = {"$regex": f"^{search_params.identification_number}", "$options": "i"}
            
        if search_params.first_name:
            filter_dict["first_name"] = {"$regex": f"^{search_params.first_name}", "$options": "i"}
        if search_params.first_lastname:
            filter_dict["first_lastname"] = {"$regex": f"^{search_params.first_lastname}", "$options": "i"}
            
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
                filter_dict["birth_date"].update(age_filter)
            else:
                filter_dict["birth_date"] = age_filter
                
        if search_params.entity:
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
            
        if hasattr(search_params, 'search') and search_params.search:
            search_term = search_params.search.strip()
            if search_term.isdigit():
                filter_dict["identification_number"] = {"$regex": f"^{search_term}", "$options": "i"}
            else:
                filter_dict["$or"] = [
                    {"first_name": {"$regex": search_term, "$options": "i"}},
                    {"first_lastname": {"$regex": search_term, "$options": "i"}},
                    {"second_name": {"$regex": search_term, "$options": "i"}},
                    {"second_lastname": {"$regex": search_term, "$options": "i"}},
                    {"identification_number": {"$regex": search_term, "$options": "i"}},
                    {"patient_code": {"$regex": search_term, "$options": "i"}}
                ]
            
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
