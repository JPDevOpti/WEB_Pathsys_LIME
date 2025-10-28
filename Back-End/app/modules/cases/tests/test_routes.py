from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.modules.cases.routes.case_routes import router, get_service
from app.modules.cases.schemas.case import (
    CaseCreate,
    CaseUpdate,
    PatientInfo,
    EntityInfo,
    CaseResponse,
)
from app.core.exceptions import BadRequestError, NotFoundError, ConflictError


def _payload():
    return CaseCreate(
        patient_info=PatientInfo(
            patient_code="",
            identification_type=1,
            identification_number="12345678",
            name="Juan Pérez",
            age=35,
            gender="Masculino",
            entity_info=EntityInfo(id="ENT-1", name="Entidad Demo"),
            care_type="Ambulatorio",
        ),
        requesting_physician="Dr. Demo",
        service="Consulta externa",
        samples=[],
    )


class FakeService:
    async def create_case(self, payload: CaseCreate) -> CaseResponse:
        return CaseResponse(
            id="656565656565656565656565",
            case_code="2025-00001",
            patient_info=payload.patient_info.model_copy(update={"patient_code": "1-12345678"}),
            requesting_physician=payload.requesting_physician,
            service=payload.service,
            samples=payload.samples or [],
            state="En proceso",
            priority="Normal",
            observations=None,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )

    async def update_case(self, code: str, payload: CaseUpdate) -> CaseResponse:
        if payload.state == "Completado":
            raise BadRequestError("Solo se pueden completar casos en estado 'Por entregar'")
        return CaseResponse(
            id="656565656565656565656565",
            case_code=code,
            patient_info=_payload().patient_info.model_copy(update={"patient_code": "1-12345678"}),
            requesting_physician="Dr. Demo",
            service="Consulta externa",
            samples=[],
            state=payload.state or "En proceso",
            priority="Normal",
            observations=None,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )

    async def delete_case(self, code: str):
        return {"deleted": True, "case_code": code}

    async def get_case(self, code: str) -> CaseResponse:
        raise NotFoundError("No encontrado")

    async def list_cases(self, **kwargs):
        return []


def create_app():
    app = FastAPI()
    app.dependency_overrides[get_service] = lambda: FakeService()
    app.include_router(router)
    return app


def test_route_create_case_success():
    app = create_app()
    client = TestClient(app)
    resp = client.post("/cases/", json=_payload().model_dump())
    assert resp.status_code == 201
    body = resp.json()
    assert body["case_code"] == "2025-00001"
    assert body["patient_info"]["patient_code"] == "1-12345678"


def test_route_update_case_completed_returns_400():
    app = create_app()
    client = TestClient(app)
    resp = client.put("/cases/2025-00001", json=CaseUpdate(state="Completado").model_dump(exclude_none=True))
    assert resp.status_code == 400


def test_route_get_case_not_found_maps_404():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/cases/NO-EXISTE")
    assert resp.status_code == 404