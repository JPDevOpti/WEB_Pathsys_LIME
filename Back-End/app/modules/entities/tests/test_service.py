import pytest
from types import SimpleNamespace

from app.modules.entities.services.entity_service import EntityService


class FakeRepo:
    def __init__(self, *_):
        self._store = {}

    async def exists_code(self, code: str) -> bool:
        return code.upper() in self._store

    async def create(self, data):
        d = data.dict()
        d["_id"] = "616161616161616161616161"
        d["id"] = d["_id"]
        self._store[d["entity_code"].upper()] = d
        return d

    async def get_by_code(self, code: str):
        return self._store.get(code.upper())

    async def list_active(self, search):
        return [v for v in self._store.values() if v.get("is_active")]

    async def list_all(self, search):
        return list(self._store.values())

    async def update_by_code(self, code: str, update):
        if code.upper() not in self._store:
            return None
        upd = {k: v for k, v in update.dict().items() if v is not None}
        new_code = (upd.get("entity_code") or code).upper()
        self._store[new_code] = {**self._store.pop(code.upper()), **upd}
        return self._store[new_code]

    async def delete_by_code(self, code: str) -> bool:
        return bool(self._store.pop(code.upper(), None))


def _payload(code="EN-01"):
    from app.modules.entities.schemas.entity import EntityCreate
    return EntityCreate(
        name="Laboratorio Central",
        entity_code=code,
        notes="Entidad de referencia",
        is_active=True,
    )


@pytest.mark.asyncio
async def test_create_success_and_conflict(monkeypatch):
    import app.modules.entities.services.entity_service as svc_mod
    monkeypatch.setattr(svc_mod, "EntityRepository", lambda db: FakeRepo())

    service = EntityService(database=SimpleNamespace())
    created = await service.create_entity(_payload("EN-01"))
    assert created.entity_code == "EN-01"

    with pytest.raises(Exception):
        await service.create_entity(_payload("EN-01"))


@pytest.mark.asyncio
async def test_get_update_delete_flow(monkeypatch):
    import app.modules.entities.services.entity_service as svc_mod
    repo = FakeRepo()
    monkeypatch.setattr(svc_mod, "EntityRepository", lambda db: repo)
    service = EntityService(database=SimpleNamespace())

    with pytest.raises(Exception):
        await service.delete_by_code("NO-EXISTE")

    await service.create_entity(_payload("EN-02"))
    got = await service.get_by_code("EN-02")
    assert got.entity_code == "EN-02"

    upd_schema = __import__("app.modules.entities.schemas.entity", fromlist=["EntityUpdate"]).EntityUpdate(notes="Actualizada")
    upd = await service.update_by_code("EN-02", update=upd_schema)
    assert upd.notes == "Actualizada"