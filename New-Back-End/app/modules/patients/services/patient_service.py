import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import PatientCreate, PatientUpdate, PatientResponse, PatientSearch
from ..repositories import PatientRepository
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = PatientRepository(database)

    async def create_patient(self, patient: PatientCreate) -> PatientResponse:
        try:
            await self._validate_patient_data(patient)
            
            existing_patient = await self.repository.get_by_id(patient.patient_code)
            if existing_patient:
                raise ConflictError(f"Patient with code {patient.patient_code} already exists")
            
            patient_data = await self.repository.create(patient)
            return PatientResponse(**patient_data)
        except ConflictError as e:
            raise
        except Exception as e:
            raise

    async def get_patient_by_code(self, patient_code: str) -> PatientResponse:
        patient_data = await self.repository.get_by_id(patient_code)
        if not patient_data:
            raise NotFoundError(f"Patient with code {patient_code} not found")
        return PatientResponse(**patient_data)

    async def update_patient(self, patient_code: str, patient_update: PatientUpdate) -> PatientResponse:
        if patient_update.age is not None and (patient_update.age < 0 or patient_update.age > 150):
            raise BadRequestError("Age must be between 0 and 150 years")
        patient_data = await self.repository.update(patient_code, patient_update)
        return PatientResponse(**patient_data)

    async def change_patient_code(self, patient_code: str, new_code: str) -> PatientResponse:
        if not new_code or len(new_code.strip()) < 6 or len(new_code.strip()) > 12:
            raise BadRequestError("Patient code must be between 6 and 12 characters")
        cases_collection = None
        try:
            cases_collection = self.repository.collection.database.cases
        except Exception:
            cases_collection = None
        patient_data = await self.repository.change_code(patient_code, new_code.strip(), cases_collection)
        return PatientResponse(**patient_data)

    async def delete_patient(self, patient_code: str) -> bool:
        patient_data = await self.repository.get_by_id(patient_code)
        if not patient_data:
            raise NotFoundError(f"Patient with code {patient_code} not found")
        result = await self.repository.delete(patient_code)
        return result

    async def list_patients(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        entity: Optional[str] = None,
        gender: Optional[str] = None,
        care_type: Optional[str] = None
    ) -> List[PatientResponse]:
        patients_data = await self.repository.list_with_filters(
            skip=skip, limit=limit, search=search, entity=entity, gender=gender, care_type=care_type
        )
        return [PatientResponse(**p) for p in patients_data]

    async def advanced_search(self, search_params: PatientSearch) -> Dict[str, Any]:
        if search_params.date_from or search_params.date_to:
            await self._validate_date_range(search_params.date_from, search_params.date_to)
        result = await self.repository.advanced_search(search_params)
        result["patients"] = [PatientResponse(**p) for p in result["patients"]]
        return result

    async def get_total_count(self) -> int:
        return await self.repository.count_total()

    async def exists(self, patient_code: str) -> bool:
        patient_data = await self.repository.get_by_id(patient_code)
        return patient_data is not None

    async def _validate_patient_data(self, patient: PatientCreate) -> None:
        if patient.age < 0 or patient.age > 150:
            raise BadRequestError("Age must be between 0 and 150 years")

    async def _validate_date_range(self, date_from: Optional[str], date_to: Optional[str]) -> None:
        if date_from and date_to:
            try:
                from datetime import datetime
                start_date = datetime.fromisoformat(date_from)
                end_date = datetime.fromisoformat(date_to)
                if start_date > end_date:
                    raise BadRequestError("Start date cannot be after end date")
            except ValueError:
                raise BadRequestError("Invalid date format. Use YYYY-MM-DD")

patient_service: Optional[PatientService] = None

def get_patient_service(database: AsyncIOMotorDatabase) -> PatientService:
    return PatientService(database)
