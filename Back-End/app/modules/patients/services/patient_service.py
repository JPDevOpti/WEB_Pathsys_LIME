from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import PatientCreate, PatientUpdate, PatientResponse, PatientSearch
from ..repositories import PatientRepository
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError
import logging

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = PatientRepository(database)

    async def create_patient(self, patient: PatientCreate) -> PatientResponse:
        try:
            patient_data = await self.repository.create(patient)
            return PatientResponse(**patient_data)
        except ConflictError:
            raise
        except Exception:
            logger.exception("[service:create] Error inesperado")
            raise

    async def get_patient_by_code(self, patient_code: str) -> PatientResponse:
        patient_data = await self.repository.get_by_id(patient_code)
        if not patient_data:
            raise NotFoundError(f"Paciente con código {patient_code} no encontrado")
        return PatientResponse(**patient_data)

    async def update_patient(self, patient_code: str, patient_update: PatientUpdate) -> PatientResponse:
        patient_data = await self.repository.update(patient_code, patient_update)
        return PatientResponse(**patient_data)

    async def change_patient_identification(self, patient_code: str, new_identification_type: str, new_identification_number: str) -> PatientResponse:
        if not new_identification_number or len(new_identification_number.strip()) == 0:
            raise BadRequestError("El número de identificación no puede estar vacío")
        
        # Usar el valor numérico si viene un Enum; si ya es str/int, conservar
        try:
            new_type_value = int(new_identification_type)
        except (TypeError, ValueError):
            new_type_value = new_identification_type
        
        new_code = f"{new_type_value}-{new_identification_number}"
        if patient_code == new_code:
            raise BadRequestError("La nueva identificación debe ser diferente a la actual")
            
        cases_collection = getattr(self.repository.collection.database, "cases", None)
        patient_data = await self.repository.change_identification(patient_code, new_type_value, new_identification_number, cases_collection)
        if not patient_data:
            raise NotFoundError("Paciente no encontrado")
        return PatientResponse(**patient_data)

    async def delete_patient(self, patient_code: str) -> bool:
        patient_data = await self.repository.get_by_id(patient_code)
        if not patient_data:
            raise NotFoundError(f"Paciente con código {patient_code} no encontrado")
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



    # Eliminado: validaciones cubiertas por Pydantic en schemas

    async def _validate_date_range(self, date_from: Optional[str], date_to: Optional[str]) -> None:
        if date_from and date_to:
            try:
                start_date = datetime.fromisoformat(date_from)
                end_date = datetime.fromisoformat(date_to)
                if start_date > end_date:
                    raise BadRequestError("La fecha inicial no puede ser posterior a la fecha final")
            except ValueError:
                raise BadRequestError("Formato de fecha inválido. Use YYYY-MM-DD")

def get_patient_service(database: AsyncIOMotorDatabase) -> PatientService:
    return PatientService(database)
