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
        if not await self.repo.validate_case_can_be_signed(case_code):
            current_state = await self.repo.get_case_state(case_code)
            if not current_state:
                raise NotFoundError(f"Caso con código {case_code} no encontrado")
            else:
                raise BadRequestError(f"No se puede firmar un caso con estado '{current_state}'. Solo se pueden firmar casos que no estén completados")
        
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
            can_sign = current_state != "Completado"
            
            if can_sign:
                message = "El caso puede ser firmado"
            else:
                message = f"No se puede firmar un caso con estado '{current_state}'. Solo se pueden firmar casos que no estén completados"
            
            return CaseSignValidation(
                case_code=case_code,
                can_sign=can_sign,
                message=message,
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
        """Convertir documento de MongoDB a CaseResponse"""
        return CaseResponse(
            id=str(doc.get("_id")),
            case_code=doc["case_code"],
            patient_info=doc["patient_info"],
            requesting_physician=doc.get("requesting_physician"),
            service=doc.get("service"),
            samples=doc.get("samples", []),
            state=doc.get("state"),
            priority=doc.get("priority"),
            observations=doc.get("observations"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            signed_at=doc.get("signed_at"),
            assigned_pathologist=doc.get("assigned_pathologist"),
            result=doc.get("result"),
        )
