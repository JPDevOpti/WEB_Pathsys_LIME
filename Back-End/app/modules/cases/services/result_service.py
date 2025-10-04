from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import NotFoundError, BadRequestError
from app.modules.cases.schemas.result import ResultUpdate, ResultResponse
from app.modules.cases.schemas.case import CaseResponse
from app.modules.cases.repositories.result_repository import ResultRepository


class ResultService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = ResultRepository(db)

    async def update_case_result(self, case_code: str, payload: ResultUpdate) -> CaseResponse:
        """Actualizar resultado de un caso"""
        
        # Validar que el caso existe y no está completado
        if not await self.repo.validate_case_not_completed(case_code):
            current_state = await self.repo.get_case_state(case_code)
            if not current_state:
                raise NotFoundError(f"Caso con código {case_code} no encontrado")
            else:
                raise BadRequestError(f"No se puede editar un caso con estado '{current_state}'. Solo se pueden editar casos en 'En proceso' o 'Por firmar'")
        
        # Preparar datos del resultado (solo campos no nulos)
        result_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        
        for field, value in payload_dict.items():
            if value is not None:
                result_data[field] = value
        
        # Actualizar el resultado
        updated_doc = await self.repo.update_result(case_code, result_data)
        
        if not updated_doc:
            raise NotFoundError(f"Caso con código {case_code} no encontrado")
        
        # Convertir a CaseResponse
        return self._to_case_response(updated_doc)

    async def get_case_result(self, case_code: str) -> Optional[Dict[str, Any]]:
        """Obtener resultado de un caso"""
        return await self.repo.get_result(case_code)

    async def validate_case_state_for_editing(self, case_code: str) -> bool:
        """Validar que el caso puede ser editado"""
        return await self.repo.validate_case_not_completed(case_code)

    def _to_case_response(self, doc: Dict[str, Any]) -> CaseResponse:
        """Convert MongoDB document to CaseResponse using only new structure"""
        # Normalize patient_info using only new structure
        patient = doc.get("patient_info") or {}
        entity_info = patient.get("entity_info") or {}
        normalized_patient = {
            "patient_code": patient.get("patient_code") or "",
            "identification_type": patient.get("identification_type") or None,
            "identification_number": patient.get("identification_number") or None,
            "name": patient.get("name") or "",
            "age": int(patient.get("age") or 0),
            "gender": patient.get("gender") or "",
            "entity_info": {
                "id": entity_info.get("id") or "",
                "name": entity_info.get("name") or "",
            },
            "care_type": patient.get("care_type") or "",
            "observations": patient.get("observations"),
        }
        # Derive patient_code if missing and identification present
        id_type = normalized_patient.get("identification_type")
        id_number = normalized_patient.get("identification_number")
        if not normalized_patient.get("patient_code") and id_type and id_number:
            normalized_patient["patient_code"] = f"{id_type}-{id_number}"

        # Use samples directly from new format
        samples = doc.get("samples") or []

        doc_out = {
            "id": str(doc.get("_id")),
            "case_code": doc.get("case_code") or "",
            "patient_info": normalized_patient,
            "requesting_physician": doc.get("requesting_physician"),
            "service": doc.get("service"),
            "samples": samples,
            "state": doc.get("state") or "En proceso",
            "priority": doc.get("priority") or "Normal",
            "observations": doc.get("observations"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "signed_at": doc.get("signed_at"),
            "assigned_pathologist": doc.get("assigned_pathologist"),
            "result": doc.get("result"),
            "delivered_to": doc.get("delivered_to"),
            "delivered_at": doc.get("delivered_at"),
            "business_days": doc.get("business_days"),
            "additional_notes": doc.get("additional_notes") or [],
            "complementary_tests": doc.get("complementary_tests") or [],
        }
        return CaseResponse(**doc_out)
