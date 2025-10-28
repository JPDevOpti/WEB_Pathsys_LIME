import pytest
from types import SimpleNamespace

from app.modules.tests.services.test_service import TestService


class FakeRepo:
    def __init__(self, *_):
        self._store = {}

    async def exists_code(self, code: str) -> bool:
        return code.upper() in self._store

    async def create(self, data):
        d = data.dict()
        d["_id"] = "606060606060606060606060"
        d["id"] = d["_id"]
        self._store[d["test_code"].upper()] = d
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
        new_code = (upd.get("test_code") or code).upper()
        self._store[new_code] = {**self._store.pop(code.upper()), **upd}
        return self._store[new_code]

    async def delete_by_code(self, code: str) -> bool:
        return bool(self._store.pop(code.upper(), None))


def _payload(code="HB-01"):
    from app.modules.tests.schemas.test import TestCreate
    return TestCreate(
        name="Hematología básica",
        test_code=code,
        description="Perfil sanguíneo estándar",
        time=30,
        price=25.5,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_create_success_and_conflict(monkeypatch):
    import app.modules.tests.services.test_service as svc_mod
    monkeypatch.setattr(svc_mod, "TestRepository", lambda db: FakeRepo())

    service = TestService(database=SimpleNamespace())
    created = await service.create_test(_payload("HB-01"))
    assert created.test_code == "HB-01"

    with pytest.raises(Exception):
        await service.create_test(_payload("HB-01"))


@pytest.mark.asyncio
async def test_get_update_delete_flow(monkeypatch):
    import app.modules.tests.services.test_service as svc_mod
    repo = FakeRepo()
    monkeypatch.setattr(svc_mod, "TestRepository", lambda db: repo)
    service = TestService(database=SimpleNamespace())

    # No existe -> not found al hacer delete
    with pytest.raises(Exception):
        await service.delete_by_code("NO-EXISTE")

    # Crear y consultar
    await service.create_test(_payload("HB-02"))
    got = await service.get_by_code("HB-02")
    assert got.test_code == "HB-02"

    # Actualizar sin conflicto
    upd = await service.update_by_code("HB-02", update=__import__("app.modules.tests.schemas.test", fromlist=["TestUpdate"]).TestUpdate(description="Actualizada"))
    assert upd.description == "Actualizada"