from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import NotFoundError, ConflictError
from app.modules.cases.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.repositories.consecutive_repository import CaseConsecutiveRepository


class CaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CaseRepository(db)
        self.seq = CaseConsecutiveRepository(db)

    async def init_indexes(self):
        await self.repo.ensure_indexes()
        await self.seq.ensure_indexes()

    async def create_case(self, payload: CaseCreate) -> CaseResponse:
        await self.init_indexes()
        year = datetime.utcnow().year
        for _ in range(3):
            case_code = await self.seq.generate_case_code(year)
            data = payload.model_dump()
            data["case_code"] = case_code
            try:
                doc = await self.repo.create(data)
                return self._to_response(doc)
            except Exception as e:
                if "duplicate key error" in str(e).lower():
                    continue
                raise
        raise ConflictError("Failed to generate unique case_code after retries")

    async def update_case(self, case_code: str, payload: CaseUpdate) -> CaseResponse:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Case with code {case_code} not found")
        updated = await self.repo.update_by_case_code(case_code, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete_case(self, case_code: str) -> Dict[str, Any]:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Case with code {case_code} not found")
        ok = await self.repo.delete_by_case_code(case_code)
        return {"deleted": ok, "case_code": case_code}

    async def get_case(self, case_code: str) -> CaseResponse:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Case with code {case_code} not found")
        return self._to_response(doc)

    def _to_response(self, doc: Dict[str, Any]) -> CaseResponse:
        doc_out = {
            "id": str(doc.get("_id")),
            "case_code": doc["case_code"],
            "patient_info": doc["patient_info"],
            "requesting_physician": doc.get("requesting_physician"),
            "service": doc.get("service"),
            "samples": doc.get("samples", []),
            "state": doc.get("state"),
            "priority": doc.get("priority"),
            "observations": doc.get("observations"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
        return CaseResponse(**doc_out)


