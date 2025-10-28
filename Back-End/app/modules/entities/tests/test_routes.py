from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.entities.routes.entity_routes import router, get_service
from app.modules.entities.services.entity_service import EntityService
from app.modules.entities.schemas.entity import EntityCreate, EntityUpdate, EntityResponse, EntitySearch
from app.core.exceptions import NotFoundError, ConflictError


class FakeService(EntityService):
    def __init__(self):
        self._store = {}

    async def create_entity(self, data: EntityCreate) -> EntityResponse:
        code = data.entity_code.upper()
        if code in self._store:
            raise ConflictError("Entidad duplicada")
        doc = {
            "id": "616161616161616161616161",
            "name": data.name,
            "entity_code": code,
            "notes": data.notes,
            "is_active": data.is_active,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        self._store[code] = doc
        return EntityResponse(**doc)

    async def get_by_code(self, code: str) -> EntityResponse:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrada")
        return EntityResponse(**self._store[code])

    async def list_active(self, search: EntitySearch):
        return [EntityResponse(**d) for d in self._store.values() if d.get("is_active")]

    async def list_all(self, search: EntitySearch):
        return [EntityResponse(**d) for d in self._store.values()]

    async def update_by_code(self, code: str, update: EntityUpdate) -> EntityResponse:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrada")
        upd = update.dict(exclude_none=True)
        if "entity_code" in upd and upd["entity_code"].upper() != code and upd["entity_code"].upper() in self._store:
            raise ConflictError("Código duplicado")
        new_code = upd.get("entity_code", code).upper()
        self._store[new_code] = {**self._store.pop(code), **upd, "entity_code": new_code}
        return EntityResponse(**self._store[new_code])

    async def delete_by_code(self, code: str) -> bool:
        code = code.upper()
        if code not in self._store:
            raise NotFoundError("No encontrada")
        self._store.pop(code)
        return True


def create_app():
    app = FastAPI()
    # Usar una instancia singleton del servicio falso por test
    service = FakeService()
    app.dependency_overrides[get_service] = lambda: service
    app.include_router(router, prefix="/entities")
    return app


def _payload():
    return EntityCreate(
        name="Laboratorio Central",
        entity_code="EN-01",
        notes="Entidad de referencia",
        is_active=True,
    )


def test_route_create_success_and_conflict():
    app = create_app()
    client = TestClient(app)
    r1 = client.post("/entities/", json=_payload().model_dump())
    assert r1.status_code == 201
    r2 = client.post("/entities/", json=_payload().model_dump())
    assert r2.status_code == 409


def test_route_get_not_found():
    app = create_app()
    client = TestClient(app)
    r = client.get("/entities/NO-EXISTE")
    assert r.status_code == 404


def test_route_update_and_delete():
    app = create_app()
    client = TestClient(app)
    client.post("/entities/", json=_payload().model_dump())
    u = client.put("/entities/EN-01", json=EntityUpdate(notes="Actualizada").model_dump(exclude_none=True))
    assert u.status_code == 200
    d = client.delete("/entities/EN-01")
    assert d.status_code == 200