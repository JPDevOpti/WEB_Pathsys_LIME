"""Repositorio para solicitudes de aprobación."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shared.repositories.base import BaseRepository
from app.modules.approvals.models.approval_request import ApprovalRequest, ApprovalStateEnum
from app.modules.approvals.schemas.approval import ApprovalRequestSearch


class ApprovalRepository(BaseRepository[ApprovalRequest, dict, dict]):
    """Repositorio para operaciones CRUD de solicitudes de aprobación."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "approval_requests", ApprovalRequest)

    async def ensure_indexes(self):
        """Crear índices necesarios."""
        await self.collection.create_index("approval_code", unique=True)
        await self.collection.create_index("original_case_code", unique=True)
        await self.collection.create_index("approval_state")
        await self.collection.create_index("created_at", -1)

    async def get_by_approval_code(self, approval_code: str) -> Optional[ApprovalRequest]:
        """Obtener solicitud por código de aprobación."""
        doc = await self.collection.find_one({"approval_code": approval_code})
        return ApprovalRequest(**doc) if doc else None

    async def get_by_original_case_code(self, original_case_code: str) -> Optional[ApprovalRequest]:
        """Obtener solicitud por código del caso original."""
        doc = await self.collection.find_one({"original_case_code": original_case_code})
        return ApprovalRequest(**doc) if doc else None

    async def get_by_original_case_code_with_id(self, original_case_code: str) -> tuple[Optional[dict], Optional[ApprovalRequest]]:
        """Obtener solicitud por código del caso original con ID del documento."""
        doc = await self.collection.find_one({"original_case_code": original_case_code})
        if doc:
            return doc, ApprovalRequest(**doc)
        return None, None

    async def _build_search_query(self, search_params: ApprovalRequestSearch) -> Dict[str, Any]:
        """Construir query de búsqueda."""
        q: Dict[str, Any] = {}
        if search_params.original_case_code:
            q["original_case_code"] = {"$regex": search_params.original_case_code, "$options": "i"}
        if search_params.approval_state:
            q["approval_state"] = search_params.approval_state.value
        if search_params.request_date_from or search_params.request_date_to:
            f: Dict[str, Any] = {}
            if search_params.request_date_from:
                f["$gte"] = search_params.request_date_from
            if search_params.request_date_to:
                f["$lte"] = search_params.request_date_to
            q["approval_info.request_date"] = f
        return q

    async def search(self, search_params: ApprovalRequestSearch, skip: int = 0, limit: int = 50) -> List[ApprovalRequest]:
        """Buscar solicitudes con filtros."""
        q = await self._build_search_query(search_params)
        cursor = self.collection.find(q).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        result = []
        for d in docs:
            d['id'] = str(d['_id'])
            result.append(ApprovalRequest(**d))
        return result

    async def count(self, search_params: ApprovalRequestSearch) -> int:
        """Contar solicitudes que coinciden con los filtros."""
        q = await self._build_search_query(search_params)
        return await self.collection.count_documents(q)

    async def get_by_state(self, state: ApprovalStateEnum, limit: int = 50) -> List[ApprovalRequest]:
        """Obtener solicitudes por estado."""
        cursor = self.collection.find({"approval_state": state.value}).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        result = []
        for d in docs:
            d['id'] = str(d['_id'])
            result.append(ApprovalRequest(**d))
        return result

    async def update_state(self, approval_code: str, new_state: ApprovalStateEnum) -> bool:
        """Actualizar estado de una solicitud."""
        update_data = {
            "approval_state": new_state.value,
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.update_one(
            {"approval_code": approval_code}, 
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def update_complementary_tests(self, approval_code: str, complementary_tests: list) -> Optional[ApprovalRequest]:
        """Actualizar pruebas complementarias de una solicitud."""
        update_data = {
            "complementary_tests": complementary_tests,
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.update_one(
            {"approval_code": approval_code}, 
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_approval_code(approval_code)
        return None

    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas agregadas."""
        try:
            pipeline = [{"$group": {"_id": "$approval_state", "count": {"$sum": 1}}}]
            res = await self.collection.aggregate(pipeline).to_list(length=None)
            stats = {
                "total_requests": 0,
                "requests_made": 0,
                "pending_approval": 0,
                "approved": 0,
                "rejected": 0
            }
            for it in res:
                estado, count = it.get("_id"), it.get("count", 0)
                stats["total_requests"] += count
                if estado == ApprovalStateEnum.REQUEST_MADE.value:
                    stats["requests_made"] = count
                elif estado == ApprovalStateEnum.PENDING_APPROVAL.value:
                    stats["pending_approval"] = count
                elif estado == ApprovalStateEnum.APPROVED.value:
                    stats["approved"] = count
                elif estado == ApprovalStateEnum.REJECTED.value:
                    stats["rejected"] = count
            return stats
        except Exception as e:
            print(f"Error en get_stats: {e}")
            return {
                "total_requests": 0,
                "requests_made": 0,
                "pending_approval": 0,
                "approved": 0,
                "rejected": 0
            }

    async def update_by_approval_code(self, approval_code: str, update_data: dict) -> Optional[ApprovalRequest]:
        """Actualizar solicitud por código."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.collection.find_one_and_update(
            {"approval_code": approval_code},
            {"$set": update_data},
            return_document=True
        )
        return ApprovalRequest(**result) if result else None

    async def delete_by_approval_code(self, approval_code: str) -> bool:
        """Eliminar solicitud por código."""
        result = await self.collection.delete_one({"approval_code": approval_code})
        return result.deleted_count > 0
