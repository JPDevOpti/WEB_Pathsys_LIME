"""Servicio para solicitudes de aprobación."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.modules.approvals.models.approval_request import ApprovalRequest, ApprovalStateEnum, ApprovalInfo, AssignedPathologistInfo
from app.modules.approvals.schemas.approval import (
    ApprovalRequestCreate,
    ApprovalRequestUpdate,
    ApprovalRequestResponse,
    ApprovalRequestSearch,
    ApprovalStats
)
from app.modules.approvals.repositories.approval_repository import ApprovalRepository
from app.modules.approvals.repositories.consecutive_repository import ApprovalConsecutiveRepository
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.repositories.consecutive_repository import CaseConsecutiveRepository
from app.modules.cases.schemas.case import CaseCreate, SampleInfo, PatientInfo as CasePatientInfo
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


class ApprovalService:
    """Servicio para lógica de negocio de solicitudes de aprobación."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.repository = ApprovalRepository(database)
        self.consecutive_repo = ApprovalConsecutiveRepository(database)
        self.case_repository = CaseRepository(database)
        self.case_consecutive_repo = CaseConsecutiveRepository(database)

    def _clean_object_ids(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir ObjectIds a strings para serialización JSON."""
        if not data:
            return data
        
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                cleaned[key] = str(value)
            elif isinstance(value, dict):
                cleaned[key] = self._clean_object_ids(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    self._clean_object_ids(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item
                    for item in value
                ]
            else:
                cleaned[key] = value
        
        return cleaned

    def _map(self, approval: ApprovalRequest) -> ApprovalRequestResponse:
        """Mapear modelo a respuesta."""
        data = {
            "id": approval.id or str(getattr(approval, '_id', '')),
            "approval_code": approval.approval_code,
            "original_case_code": approval.original_case_code,
            "approval_state": approval.approval_state,
            "complementary_tests": [p.model_dump() if hasattr(p, 'model_dump') else p for p in approval.complementary_tests],
            "approval_info": approval.approval_info.model_dump() if approval.approval_info else None,
            "created_at": approval.created_at,
            "updated_at": approval.updated_at,
        }
        return ApprovalRequestResponse.model_validate(data)

    async def create_approval_request(self, approval_data: ApprovalRequestCreate) -> ApprovalRequestResponse:
        """Crear nueva solicitud de aprobación."""
        # Verificar que el caso original existe
        original_case = await self.case_repository.get_by_case_code(approval_data.original_case_code)
        if not original_case:
            raise NotFoundError(f"Caso {approval_data.original_case_code} no encontrado")
        
        # Verificar que no existe una solicitud activa para este caso
        existing = await self.repository.get_by_original_case_code(approval_data.original_case_code)
        if existing:
            raise ConflictError(f"Ya existe una solicitud de aprobación para el caso {approval_data.original_case_code}")
        
        # Generar código de aprobación
        approval_code = await self.consecutive_repo.generate_approval_code()
        
        # Obtener información del patólogo asignado del caso original
        assigned_pathologist_info = None
        if original_case.get("assigned_pathologist"):
            assigned_pathologist_info = AssignedPathologistInfo(
                id=original_case["assigned_pathologist"]["id"],
                name=original_case["assigned_pathologist"]["name"]
            )
        
        # Crear información de aprobación
        approval_info = ApprovalInfo(
            reason=approval_data.reason,
            assigned_pathologist=assigned_pathologist_info
        )
        
        # Crear solicitud
        new_request = ApprovalRequest(
            approval_code=approval_code,
            original_case_code=approval_data.original_case_code,
            approval_state=ApprovalStateEnum.REQUEST_MADE,
            complementary_tests=approval_data.complementary_tests,
            approval_info=approval_info
        )
        
        created = await self.repository.create(new_request.model_dump(by_alias=False))
        return self._map(created)

    async def get_approval_by_code(self, approval_code: str) -> Optional[ApprovalRequestResponse]:
        """Obtener solicitud por código."""
        approval = await self.repository.get_by_approval_code(approval_code)
        return self._map(approval) if approval else None

    async def search_approvals(self, search_params: ApprovalRequestSearch, skip: int = 0, limit: int = 50) -> List[ApprovalRequestResponse]:
        """Buscar solicitudes con filtros."""
        approvals = await self.repository.search(search_params, skip, limit)
        return [self._map(approval) for approval in approvals]

    async def count_approvals(self, search_params: ApprovalRequestSearch) -> int:
        """Contar solicitudes que coinciden con los filtros."""
        return await self.repository.count(search_params)

    async def get_approvals_by_state(self, state: ApprovalStateEnum, limit: int = 50) -> List[ApprovalRequestResponse]:
        """Obtener solicitudes por estado."""
        approvals = await self.repository.get_by_state(state, limit)
        return [self._map(approval) for approval in approvals]

    async def manage_approval(self, approval_code: str) -> Optional[ApprovalRequestResponse]:
        """Marcar solicitud como en gestión."""
        success = await self.repository.update_state(approval_code, ApprovalStateEnum.PENDING_APPROVAL)
        return await self.get_approval_by_code(approval_code) if success else None

    async def approve_request(self, approval_code: str) -> Optional[Dict[str, Any]]:
        """Aprobar solicitud y crear nuevo caso automáticamente."""
        # Actualizar estado a aprobado
        success = await self.repository.update_state(approval_code, ApprovalStateEnum.APPROVED)
        if not success:
            return None

        # Crear automáticamente un nuevo caso
        try:
            approval = await self.repository.get_by_approval_code(approval_code)
            if not approval:
                return {"approval": await self.get_approval_by_code(approval_code), "new_case": None}

            # Obtener caso original
            original_case = await self.case_repository.get_by_case_code(approval.original_case_code)
            if not original_case:
                return {"approval": await self.get_approval_by_code(approval_code), "new_case": None}

            # Generar nuevo código de caso
            year = datetime.utcnow().year
            new_case_code = await self.case_consecutive_repo.generate_case_code(year)

            # Preparar muestras con pruebas complementarias
            region = "General"
            if original_case.get("samples") and len(original_case["samples"]) > 0:
                region = original_case["samples"][0]["body_region"]

            # Convertir pruebas complementarias a formato de caso
            tests = []
            for test in approval.complementary_tests:
                tests.append({
                    "id": test.code,
                    "name": test.name,
                    "quantity": test.quantity
                })

            new_samples = [SampleInfo(body_region=region, tests=tests)]

            # Crear objeto de caso
            patient_info = CasePatientInfo.model_validate(original_case["patient_info"])
            observations = approval.approval_info.reason if approval.approval_info else None

            new_case = CaseCreate(
                patient_info=patient_info,
                requesting_physician=original_case.get("requesting_physician"),
                service=original_case.get("service"),
                samples=new_samples,
                priority=original_case.get("priority", "Normal"),
                observations=observations
            )

            # Crear el caso con el código generado
            case_data = new_case.model_dump()
            case_data["case_code"] = new_case_code
            created_case = await self.case_repository.create(case_data)

            # Asignar patólogo si existe en el caso original
            if original_case.get("assigned_pathologist"):
                try:
                    await self.case_repository.update_by_case_code(
                        created_case["case_code"],
                        {
                            "assigned_pathologist": {
                                "id": original_case["assigned_pathologist"]["id"],
                                "name": original_case["assigned_pathologist"]["name"]
                            }
                        }
                    )
                except Exception:
                    pass  # No bloquear si falla la asignación

            approval_response = await self.get_approval_by_code(approval_code)
            
            # Limpiar ObjectIds para serialización JSON
            cleaned_case = self._clean_object_ids(created_case) if created_case else None
            
            return {"approval": approval_response, "new_case": cleaned_case}

        except Exception:
            # No bloquear la aprobación si falla la creación del caso
            approval_response = await self.get_approval_by_code(approval_code)
            return {"approval": approval_response, "new_case": None}

    async def reject_request(self, approval_code: str) -> Optional[ApprovalRequestResponse]:
        """Rechazar solicitud."""
        success = await self.repository.update_state(approval_code, ApprovalStateEnum.REJECTED)
        return await self.get_approval_by_code(approval_code) if success else None

    async def update_approval(self, approval_code: str, update_data: ApprovalRequestUpdate) -> Optional[ApprovalRequestResponse]:
        """Actualizar solicitud."""
        # Verificar que la solicitud existe
        approval = await self.repository.get_by_approval_code(approval_code)
        if not approval:
            return None
        
        # Solo permitir edición si está en estado "request_made"
        if approval.approval_state != ApprovalStateEnum.REQUEST_MADE:
            raise BadRequestError("Solo se pueden editar las solicitudes en estado 'request_made'")
        
        # Actualizar
        updated = await self.repository.update_by_approval_code(approval_code, update_data.model_dump(exclude_unset=True))
        return await self.get_approval_by_code(approval_code) if updated else None

    async def update_complementary_tests(self, approval_code: str, complementary_tests: list) -> Optional[ApprovalRequestResponse]:
        """Actualizar pruebas complementarias."""
        # Verificar que la solicitud existe y está en estado correcto
        approval = await self.repository.get_by_approval_code(approval_code)
        if not approval:
            return None
        
        if approval.approval_state != ApprovalStateEnum.REQUEST_MADE:
            raise BadRequestError("Solo se pueden editar las pruebas cuando la solicitud está en estado 'request_made'")
        
        updated = await self.repository.update_complementary_tests(approval_code, complementary_tests)
        return await self.get_approval_by_code(approval_code) if updated else None

    async def delete_approval(self, approval_code: str) -> bool:
        """Eliminar solicitud."""
        return await self.repository.delete_by_approval_code(approval_code)

    async def get_statistics(self) -> ApprovalStats:
        """Obtener estadísticas de solicitudes."""
        raw_stats = await self.repository.get_stats()
        return ApprovalStats(
            total_requests=raw_stats.get("total_requests", 0),
            requests_made=raw_stats.get("requests_made", 0),
            pending_approval=raw_stats.get("pending_approval", 0),
            approved=raw_stats.get("approved", 0),
            rejected=raw_stats.get("rejected", 0)
        )
