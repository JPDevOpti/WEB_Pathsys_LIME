from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.cases.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.repositories.consecutive_repository import CaseConsecutiveRepository
from bson import ObjectId


class CaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CaseRepository(db)
        self.seq = CaseConsecutiveRepository(db)

    # La inicialización de índices se moverá al arranque de la app

    async def create_case(self, payload: CaseCreate) -> CaseResponse:
        year = datetime.now(timezone.utc).year
        for _ in range(3):
            case_code = await self.seq.generate_case_code(year)
            data = payload.model_dump()
            data["case_code"] = case_code

            # Normalizar patient_code canónico desde identificación
            patient_info = data.get("patient_info") or {}
            if patient_info:
                id_type = patient_info.get("identification_type")
                id_number = patient_info.get("identification_number")
                if id_type and id_number:
                    if not patient_info.get("patient_code"):
                        patient_info["patient_code"] = f"{id_type}-{id_number}"
                data["patient_info"] = patient_info

            try:
                doc = await self.repo.create(data)
                return self._to_response(doc)
            except Exception as e:
                if "duplicate key error" in str(e).lower():
                    continue
                raise
        raise ConflictError("No se pudo generar un código único de caso después de varios intentos")

    async def update_case(self, case_code: str, payload: CaseUpdate) -> CaseResponse:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Caso con código {case_code} no encontrado")
        
        # Validate only cases in 'Por entregar' can be marked as completed
        if payload.state == "Completado":
            current_state = doc.get("state") or "En proceso"
            if current_state != "Por entregar":
                raise BadRequestError(f"No se puede marcar como completado el caso {case_code} que está en estado '{current_state}'. Solo se pueden completar casos en estado 'Por entregar'.")
        
        updated = await self.repo.update_by_case_code(case_code, payload.model_dump(exclude_unset=True))
        return self._to_response(updated)

    async def delete_case(self, case_code: str) -> Dict[str, Any]:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Caso con código {case_code} no encontrado")
        ok = await self.repo.delete_by_case_code(case_code)
        return {"deleted": ok, "case_code": case_code}

    async def get_case(self, case_code: str) -> CaseResponse:
        doc = await self.repo.get_by_case_code(case_code)
        if not doc:
            raise NotFoundError(f"Caso con código {case_code} no encontrado")
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
        date_to: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> List[CaseResponse]:
        """Listar casos con filtros opcionales"""
        # Índices inicializados en el arranque; no repetir aquí
        
        # Construir filtros de MongoDB
        filters = {}
        
        # Filtro de búsqueda general (nombre, documento o código de caso)
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            filters["$or"] = [
                {"case_code": search_regex},
                {"patient_info.name": search_regex},
                {"patient_info.patient_code": search_regex},
                {"patient_info.identification_number": search_regex}
            ]
        
        # Filtro por patólogo explícito
        if pathologist:
            filters["assigned_pathologist.name"] = {"$regex": pathologist, "$options": "i"}
        else:
            # Si no se envía filtro de patólogo y el usuario autenticado es patólogo,
            # restringir por defecto a sus últimos casos (100 por defecto en limit)
            if current_user_id:
                # Obtener usuario para conocer rol y pathologist_code (convertir a ObjectId)
                try:
                    oid = ObjectId(current_user_id)
                except Exception:
                    oid = None
                user_doc = None
                if oid is not None:
                    user_doc = await self.db.users.find_one({"_id": oid, "is_active": True})
                if user_doc and str(user_doc.get("role", "")).lower() == "pathologist":
                    pathologist_code = user_doc.get("pathologist_code")
                    if pathologist_code:
                        # Filtrar por código de patólogo asignado
                        filters["assigned_pathologist.id"] = pathologist_code
        
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
        # Normalize patient_info using only new structure (no legacy fallbacks)
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
        # Derive patient_code if missing and identification is present
        id_type = normalized_patient.get("identification_type")
        id_number = normalized_patient.get("identification_number")
        if not normalized_patient.get("patient_code") and id_type and id_number:
            normalized_patient["patient_code"] = f"{id_type}-{id_number}"

        # Use samples only from new structure
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


