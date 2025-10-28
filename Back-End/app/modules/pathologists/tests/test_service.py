import pytest
from types import SimpleNamespace
from datetime import datetime, timezone

from app.modules.pathologists.services.pathologist_service import PathologistService
from app.modules.pathologists.schemas.pathologist import PathologistCreate, PathologistUpdate


class FakeRepo:
    def __init__(self, db):
        self.collection = SimpleNamespace()
        self._store = {}

    async def create(self, data):
        data = dict(data)
        data["_id"] = "656565656565656565656565"
        data.setdefault("created_at", datetime.now(timezone.utc))
        data.setdefault("updated_at", datetime.now(timezone.utc))
        # Simula conversión del repositorio a respuesta con 'id'
        data["id"] = str(data["_id"]) 
        self._store[data["pathologist_code"]] = data
        return data

    async def get_by_pathologist_code(self, code):
        return self._store.get(code)

    async def get_by_email(self, email):
        for doc in self._store.values():
            if doc.get("pathologist_email") == email:
                return doc
        return None

    async def get_by_medical_license(self, ml):
        for doc in self._store.values():
            if doc.get("medical_license") == ml:
                return doc
        return None

    async def update_by_pathologist_code(self, code, update):
        self._store[code] = {**self._store.get(code, {}), **update}
        return self._store[code]

    async def delete_by_pathologist_code(self, code):
        return bool(self._store.pop(code, None))


class FakeUMS:
    def __init__(self, db):
        pass

    async def create_user_for_pathologist(self, **kwargs):
        return {"created": True, **kwargs}

    async def update_user_for_pathologist(self, **kwargs):
        return {"updated": True, **kwargs}


def _payload(code="P-0001", email="demo@pathsys.io", license_="ML-12345"):
    return PathologistCreate(
        pathologist_code=code,
        pathologist_name="Dra. Demo",
        initials="DD",
        pathologist_email=email,
        medical_license=license_,
        is_active=True,
        signature="",
        observations=None,
        password="secret123",
    )


@pytest.mark.asyncio
async def test_create_pathologist_success(monkeypatch):
    import app.modules.pathologists.services.pathologist_service as svc_mod
    monkeypatch.setattr(svc_mod, "PathologistRepository", lambda db: FakeRepo(db))
    monkeypatch.setattr(svc_mod, "UserManagementService", lambda db: FakeUMS(db))

    service = PathologistService(db=SimpleNamespace(users=None))
    resp = await service.create_pathologist(_payload())
    assert resp.pathologist_code == "P-0001"
    assert resp.pathologist_email == "demo@pathsys.io"


@pytest.mark.asyncio
async def test_update_pathologist_conflict_email_raises(monkeypatch):
    import app.modules.pathologists.services.pathologist_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "PathologistRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "UserManagementService", lambda db: FakeUMS(db))

    service = PathologistService(db=SimpleNamespace(users=None))
    # Crea inicial con un email
    await service.create_pathologist(_payload(email="first@pathsys.io"))
    # Simula otro registro con email diferente existente en el sistema
    repo._store["P-OTHER"] = dict(repo._store["P-0001"], pathologist_code="P-OTHER", pathologist_email="second@pathsys.io")

    with pytest.raises(Exception) as exc:
        await service.update_pathologist("P-0001", PathologistUpdate(pathologist_email="second@pathsys.io"))
    assert "Email already exists" in str(exc.value)


@pytest.mark.asyncio
async def test_delete_pathologist_success(monkeypatch):
    import app.modules.pathologists.services.pathologist_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "PathologistRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "UserManagementService", lambda db: FakeUMS(db))

    service = PathologistService(db=SimpleNamespace(users=None))
    created = await service.create_pathologist(_payload())
    out = await service.delete_pathologist(created.pathologist_code)
    assert out["deleted"] is True
    assert out["pathologist_code"] == created.pathologist_code