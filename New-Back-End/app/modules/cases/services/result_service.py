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
            assigned_pathologist=doc.get("assigned_pathologist"),
            result=doc.get("result"),
        )
