from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.residents.routes.resident_routes import router, get_resident_service
from app.modules.residents.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    ResidentResponse,
    ResidentSearch,
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


class FakeService:
    async def create_resident(self, payload: ResidentCreate) -> ResidentResponse:
        return ResidentResponse(
            id="656565656565656565656565",
            resident_code=payload.resident_code,
            resident_name=payload.resident_name,
            initials=payload.initials,
            resident_email=payload.resident_email,
            medical_license=payload.medical_license,
            is_active=payload.is_active,
            observations=payload.observations,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def get_resident(self, resident_code: str) -> ResidentResponse:
        if resident_code == "NO-EXISTE":
            raise NotFoundError("Resident not found")
        return ResidentResponse(
            id="656565656565656565656565",
            resident_code=resident_code,
            resident_name="Dr. Residente Demo",
            initials="DRD",
            resident_email="residente@pathsys.io",
            medical_license="RML-12345",
            is_active=True,
            observations=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def update_resident(self, resident_code: str, payload: ResidentUpdate) -> ResidentResponse:
        return await self.get_resident(resident_code)

    async def delete_resident(self, resident_code: str):
        if resident_code == "NO-EXISTE":
            raise NotFoundError("Resident not found")
        return {"deleted": True, "resident_code": resident_code}


def create_app():
    app = FastAPI()
    app.dependency_overrides[get_resident_service] = lambda: FakeService()
    app.include_router(router, prefix="/residents")
    return app


def _payload():
    return ResidentCreate(
        resident_code="R-0001",
        resident_name="Dr. Residente Demo",
        initials="DRD",
        resident_email="residente@pathsys.io",
        medical_license="RML-12345",
        is_active=True,
        observations="",
        password="secret123",
    )


def test_route_create_resident_success():
    app = create_app()
    client = TestClient(app)
    resp = client.post("/residents/", json=_payload().model_dump())
    assert resp.status_code == 201
    body = resp.json()
    assert body["resident_code"] == "R-0001"
    assert body["resident_email"] == "residente@pathsys.io"


def test_route_get_resident_not_found_maps_404():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/residents/NO-EXISTE")
    assert resp.status_code == 404


def test_route_update_resident_success():
    app = create_app()
    client = TestClient(app)
    resp = client.put("/residents/R-0001", json=ResidentUpdate(resident_name="Nuevo").model_dump(exclude_none=True))
    assert resp.status_code == 200
    data = resp.json()
    assert data["resident_code"] == "R-0001"


def test_route_delete_resident_success():
    app = create_app()
    client = TestClient(app)
    resp = client.delete("/residents/R-0001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["deleted"] is True
    assert data["resident_code"] == "R-0001"