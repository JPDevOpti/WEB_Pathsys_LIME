from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
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

    async def list_cases(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        pathologist: Optional[str] = None,
        entity: Optional[str] = None,
        state: Optional[str] = None,
        test: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[CaseResponse]:
        """Listar casos con filtros opcionales"""
        await self.init_indexes()
        
        # Construir filtros de MongoDB
        filters = {}
        
        # Filtro de búsqueda general (nombre, documento o código de caso)
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            filters["$or"] = [
                {"case_code": search_regex},
                {"patient_info.name": search_regex},
                {"patient_info.patient_code": search_regex}
            ]
        
        # Filtro por patólogo
        if pathologist:
            filters["assigned_pathologist.name"] = {"$regex": pathologist, "$options": "i"}
        
        # Filtro por entidad
        if entity:
            filters["patient_info.entity_info.name"] = {"$regex": entity, "$options": "i"}
        
        # Filtro por estado
        if state:
            filters["state"] = state
        
        # Filtro por prueba específica
        if test:
            filters["samples.tests.id"] = test
        
        # Filtro por rango de fechas
        if date_from or date_to:
            date_filter = {}
            if date_from:
                try:
                    date_from_dt = datetime.fromisoformat(date_from)
                    date_filter["$gte"] = date_from_dt
                except ValueError:
                    raise BadRequestError("Formato de fecha inválido para date_from. Use YYYY-MM-DD")
            if date_to:
                try:
                    date_to_dt = datetime.fromisoformat(date_to)
                    # Incluir todo el día
                    date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    date_filter["$lte"] = date_to_dt
                except ValueError:
                    raise BadRequestError("Formato de fecha inválido para date_to. Use YYYY-MM-DD")
            filters["created_at"] = date_filter
        
        # Ejecutar consulta con paginación
        cursor = self.repo.collection.find(filters).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        # Convertir a CaseResponse
        return [self._to_response(doc) for doc in docs]

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
            "signed_at": doc.get("signed_at"),
            "assigned_pathologist": doc.get("assigned_pathologist"),
            "result": doc.get("result"),
        }
        return CaseResponse(**doc_out)


