from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import NotFoundError, BadRequestError
from app.modules.cases.schemas.sign import CaseSignRequest, CaseSignResponse, CaseSignValidation
from app.modules.cases.schemas.case import CaseResponse
from app.modules.cases.repositories.sign_repository import SignRepository


class SignService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SignRepository(db)

    async def sign_case(self, case_code: str, payload: CaseSignRequest) -> CaseResponse:
        """Firmar un caso cambiando su estado de 'Por firmar' a 'Por entregar'"""
        
        # Validar que el caso existe y puede ser firmado
        validation_result = await self.validate_case_for_signing(case_code)
        if not validation_result.can_sign:
            if validation_result.current_state is None:
                raise NotFoundError(validation_result.message)
            else:
                raise BadRequestError(validation_result.message)
        
        # Preparar datos del resultado (solo campos no nulos)
        sign_data = {}
        payload_dict = payload.model_dump(exclude_unset=True)
        
        for field, value in payload_dict.items():
            if value is not None:
                sign_data[field] = value
        
        # Firmar el caso
        updated_doc = await self.repo.sign_case(case_code, sign_data)
        
        if not updated_doc:
            raise NotFoundError(f"Caso con código {case_code} no encontrado")
        
        # Convertir a CaseResponse
        return self._to_case_response(updated_doc)

    async def validate_case_for_signing(self, case_code: str) -> CaseSignValidation:
        """Validar si un caso puede ser firmado"""
        try:
            case_doc = await self.repo.get_case_for_signing(case_code)
            
            if not case_doc:
                return CaseSignValidation(
                    case_code=case_code,
                    can_sign=False,
                    message="Caso no encontrado",
                    current_state=None
                )
            
            current_state = case_doc.get("state")
            assigned_pathologist = case_doc.get("assigned_pathologist")
            
            # Validar estado
            if current_state == "Completado":
                return CaseSignValidation(
                    case_code=case_code,
                    can_sign=False,
                    message=f"No se puede firmar un caso con estado '{current_state}'. Solo se pueden firmar casos que no estén completados",
                    current_state=current_state
                )
            
            # Validar patólogo asignado
            if not assigned_pathologist or not assigned_pathologist.get("name"):
                return CaseSignValidation(
                    case_code=case_code,
                    can_sign=False,
                    message="No se puede firmar un caso que no tenga un patólogo asignado. Contacta al auxiliar administrativo para asignar un patólogo",
                    current_state=current_state
                )
            
            return CaseSignValidation(
                case_code=case_code,
                can_sign=True,
                message="El caso puede ser firmado",
                current_state=current_state
            )
            
        except Exception as e:
            return CaseSignValidation(
                case_code=case_code,
                can_sign=False,
                message=f"Error al validar el caso: {str(e)}",
                current_state=None
            )

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

        # Use samples from new format
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
