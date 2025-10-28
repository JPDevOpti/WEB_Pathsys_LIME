from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.pathologists.routes.pathologist_routes import router, get_pathologist_service
from app.modules.pathologists.schemas.pathologist import (
    PathologistCreate,
    PathologistUpdate,
    PathologistResponse,
    SignatureUpdate,
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


def _payload():
    return PathologistCreate(
        pathologist_code="P-0001",
        pathologist_name="Dra. Demo",
        initials="DD",
        pathologist_email="demo@pathsys.io",
        medical_license="ML-12345",
        is_active=True,
        signature="",
        observations=None,
        password="secret123",
    )


class FakeService:
    async def create_pathologist(self, payload: PathologistCreate) -> PathologistResponse:
        return PathologistResponse(
            id="656565656565656565656565",
            pathologist_code=payload.pathologist_code,
            pathologist_name=payload.pathologist_name,
            initials=payload.initials,
            pathologist_email=payload.pathologist_email,
            medical_license=payload.medical_license,
            is_active=payload.is_active,
            signature=payload.signature or "",
            observations=payload.observations,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )

    async def update_pathologist(self, code: str, payload: PathologistUpdate) -> PathologistResponse:
        if payload.pathologist_email == "exists@pathsys.io":
            raise ConflictError("Email already exists")
        return PathologistResponse(
            id="656565656565656565656565",
            pathologist_code=code,
            pathologist_name=payload.pathologist_name or "Dra. Demo",
            initials=payload.initials or "DD",
            pathologist_email=payload.pathologist_email or "demo@pathsys.io",
            medical_license=payload.medical_license or "ML-12345",
            is_active=payload.is_active if payload.is_active is not None else True,
            signature=payload.signature or "",
            observations=payload.observations,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )

    async def delete_pathologist(self, code: str):
        return {"deleted": True, "pathologist_code": code}

    async def get_pathologist(self, code: str) -> PathologistResponse:
        raise NotFoundError("No encontrado")

    async def list_pathologists(self, **kwargs):
        return []

    async def update_signature(self, code: str, signature_url: str) -> PathologistResponse:
        return PathologistResponse(
            id="656565656565656565656565",
            pathologist_code=code,
            pathologist_name="Dra. Demo",
            initials="DD",
            pathologist_email="demo@pathsys.io",
            medical_license="ML-12345",
            is_active=True,
            signature=signature_url,
            observations=None,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )

    async def upload_signature_file(self, pathologist_code: str, file_content: bytes, filename: str) -> PathologistResponse:
        signature_url = f"/uploads/signatures/{filename}"
        return PathologistResponse(
            id="656565656565656565656565",
            pathologist_code=pathologist_code,
            pathologist_name="Dra. Demo",
            initials="DD",
            pathologist_email="demo@pathsys.io",
            medical_license="ML-12345",
            is_active=True,
            signature=signature_url,
            observations=None,
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
        )


def create_app():
    app = FastAPI()
    app.dependency_overrides[get_pathologist_service] = lambda: FakeService()
    app.include_router(router, prefix="/pathologists")
    return app


def test_route_create_pathologist_success():
    app = create_app()
    client = TestClient(app)
    resp = client.post("/pathologists/", json=_payload().model_dump())
    assert resp.status_code == 201
    body = resp.json()
    assert body["pathologist_code"] == "P-0001"
    assert body["pathologist_email"] == "demo@pathsys.io"


def test_route_update_pathologist_conflict_maps_409():
    app = create_app()
    client = TestClient(app)
    update = PathologistUpdate(pathologist_email="exists@pathsys.io")
    resp = client.put("/pathologists/P-0001", json=update.model_dump(exclude_none=True))
    assert resp.status_code == 409


def test_route_get_pathologist_not_found_maps_404():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/pathologists/NO-EXISTE")
    assert resp.status_code == 404


def test_route_update_signature_success():
    app = create_app()
    client = TestClient(app)
    resp = client.put("/pathologists/P-0001/signature", json=SignatureUpdate(signature="/uploads/signatures/P-0001.png").model_dump())
    assert resp.status_code == 200
    data = resp.json()
    assert data["signature"].endswith("P-0001.png")


def test_route_upload_signature_success_with_file():
    app = create_app()
    client = TestClient(app)
    # Simula archivo válido no vacío
    resp = client.put(
        "/pathologists/P-0001/upload-signature",
        files={"file": ("firma.png", b"contenido")},
    )
    assert resp.status_code == 200