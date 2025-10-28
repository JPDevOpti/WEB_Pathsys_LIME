from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.tests.routes.test_routes import router, get_service
from app.modules.tests.services.test_service import TestService
from app.modules.tests.schemas.test import TestCreate, TestUpdate, TestResponse, TestSearch
from app.core.exceptions import NotFoundError, ConflictError


class FakeService(TestService):
    def __init__(self):
        self._store = {}

    async def create_test(self, data: TestCreate) -> TestResponse:
        code = data.test_code.upper()
        if code in self._store:
            raise ConflictError("Test duplicado")
        doc = {
            "id": "606060606060606060606060",
            "name": data.name,
            "test_code": code,
            "description": data.description,
            "time": data.time,
            "price": data.price,
            "is_active": data.is_active,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        self._store[code] = doc
        return TestResponse(**doc)

    async def get_by_code(self, code: str) -> TestResponse:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrado")
        return TestResponse(**self._store[code])

    async def list_active(self, search: TestSearch):
        return [TestResponse(**d) for d in self._store.values() if d.get("is_active")]

    async def list_all(self, search: TestSearch):
        return [TestResponse(**d) for d in self._store.values()]

    async def update_by_code(self, code: str, update: TestUpdate) -> TestResponse:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrado")
        upd = update.dict(exclude_none=True)
        if "test_code" in upd and upd["test_code"].upper() != code and upd["test_code"].upper() in self._store:
            raise ConflictError("Código duplicado")
        new_code = upd.get("test_code", code).upper()
        self._store[new_code] = {**self._store.pop(code), **upd, "test_code": new_code}
        return TestResponse(**self._store[new_code])

    async def delete_by_code(self, code: str) -> bool:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrado")
        self._store.pop(code)
        return True


def create_app():
    app = FastAPI()
    # Inyectar router y sobreescribir la dependencia efectiva usada en los endpoints (get_service)
    service = FakeService()
    app.dependency_overrides[get_service] = lambda: service
    app.include_router(router, prefix="/tests")
    return app


def _payload():
    return TestCreate(
        name="Hematología básica",
        test_code="HB-01",
        description="Perfil sanguíneo estándar",
        time=30,
        price=25.5,
        is_active=True,
    )


def test_route_create_success_and_conflict():
    app = create_app()
    client = TestClient(app)
    r1 = client.post("/tests/", json=_payload().model_dump())
    assert r1.status_code == 201
    r2 = client.post("/tests/", json=_payload().model_dump())
    assert r2.status_code == 409


def test_route_get_not_found():
    app = create_app()
    client = TestClient(app)
    r = client.get("/tests/NO-EXISTE")
    assert r.status_code == 404


def test_route_update_and_delete():
    app = create_app()
    client = TestClient(app)
    client.post("/tests/", json=_payload().model_dump())
    u = client.put("/tests/HB-01", json=TestUpdate(description="Actualizada").model_dump(exclude_none=True))
    assert u.status_code == 200
    d = client.delete("/tests/HB-01")
    assert d.status_code == 200