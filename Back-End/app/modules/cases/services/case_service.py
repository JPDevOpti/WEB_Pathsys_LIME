from typing import Dict, Any, List, Optional
from datetime import datetime
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
        
        # Validar que solo se puedan marcar como completados los casos en estado "Por entregar"
        if payload.state == "Completado":
            current_state = doc.get("state") or doc.get("estado") or "En proceso"
            if current_state != "Por entregar":
                raise BadRequestError(f"No se puede marcar como completado el caso {case_code} que está en estado '{current_state}'. Solo se pueden completar casos en estado 'Por entregar'.")
        
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
        date_to: Optional[str] = None,
        current_user_id: Optional[str] = None
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
        # Normalizar patient_info para tolerar datos legacy o incompletos
        legacy_patient = doc.get("paciente") or {}
        patient = doc.get("patient_info") or {}
        entity_info = patient.get("entity_info") or legacy_patient.get("entidad_info") or {}
        normalized_patient = {
            "patient_code": patient.get("patient_code") or legacy_patient.get("paciente_code") or legacy_patient.get("cedula") or "",
            "name": patient.get("name") or legacy_patient.get("nombre") or "",
            "age": int(patient.get("age") or legacy_patient.get("edad") or 0),
            "gender": patient.get("gender") or legacy_patient.get("sexo") or "",
            "entity_info": {
                "id": entity_info.get("id") or "",
                "name": entity_info.get("name") or entity_info.get("nombre") or "",
            },
            "care_type": patient.get("care_type") or legacy_patient.get("tipo_atencion") or "",
            "observations": patient.get("observations") or legacy_patient.get("observaciones"),
        }

        # Normalizar samples/tests del documento si vienen en formato legacy
        samples = doc.get("samples")
        if not samples and doc.get("muestras"):
            samples = []
            for m in doc.get("muestras", []):
                tests = []
                for t in m.get("pruebas", []):
                    tests.append({
                        "id": t.get("id") or "",
                        "name": t.get("nombre") or "",
                        "quantity": int(t.get("cantidad") or 1),
                    })
                samples.append({
                    "body_region": m.get("region_cuerpo") or "",
                    "tests": tests,
                })

        doc_out = {
            "id": str(doc.get("_id")),
            "case_code": doc.get("case_code") or doc.get("caso_code") or "",
            "patient_info": normalized_patient,
            "requesting_physician": doc.get("requesting_physician") or (doc.get("medico_solicitante") or {}).get("nombre"),
            "service": doc.get("service") or doc.get("servicio"),
            "samples": samples or [],
            "state": doc.get("state") or doc.get("estado") or "En proceso",
            "priority": doc.get("priority") or "Normal",
            "observations": doc.get("observations") or doc.get("observaciones_generales"),
            "created_at": doc.get("created_at") or doc.get("fecha_creacion"),
            "updated_at": doc.get("updated_at") or doc.get("fecha_actualizacion"),
            "signed_at": doc.get("signed_at") or doc.get("fecha_firma"),
            "assigned_pathologist": doc.get("assigned_pathologist") or doc.get("patologo_asignado"),
            "result": doc.get("result"),
            "delivered_to": doc.get("delivered_to"),
            "delivered_at": doc.get("delivered_at"),
            "business_days": doc.get("business_days"),
            "additional_notes": doc.get("additional_notes") or [],
        }
        return CaseResponse(**doc_out)


