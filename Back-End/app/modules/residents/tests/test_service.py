import pytest
from types import SimpleNamespace
from datetime import datetime, timezone

from app.modules.residents.services.resident_service import ResidentService
from app.modules.residents.schemas.resident import ResidentCreate, ResidentUpdate


class FakeRepo:
    def __init__(self, db):
        self._store = {}

    async def get_by_resident_code(self, code):
        return self._store.get(code)

    async def get_by_email(self, email):
        for doc in self._store.values():
            if doc.get("resident_email") == email:
                return doc
        return None

    async def get_by_medical_license(self, ml):
        for doc in self._store.values():
            if doc.get("medical_license") == ml:
                return doc
        return None

    async def create(self, payload):
        data = payload.model_dump()
        data.update({
            "_id": "656565656565656565656565",
            "id": "656565656565656565656565",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        self._store[data["resident_code"]] = data
        return data

    async def update_by_resident_code(self, code, update):
        if code not in self._store:
            return None
        self._store[code] = {**self._store[code], **update}
        return self._store[code]

    async def delete_by_resident_code(self, code):
        return bool(self._store.pop(code, None))


class FakeUMS:
    def __init__(self, db):
        pass

    async def create_user_for_resident(self, **kwargs):
        return {"created": True, **kwargs}

    async def update_user_for_resident(self, **kwargs):
        return {"updated": True, **kwargs}


def _payload(code="R-0001", email="residente@pathsys.io", license_="RML-12345"):
    return ResidentCreate(
        resident_code=code,
        resident_name="Dr. Residente Demo",
        initials="DRD",
        resident_email=email,
        medical_license=license_,
        is_active=True,
        observations="",
        password="secret123",
    )


@pytest.mark.asyncio
async def test_create_resident_success(monkeypatch):
    import app.modules.residents.services.resident_service as svc_mod
    monkeypatch.setattr(svc_mod, "ResidentRepository", lambda db: FakeRepo(db))
    monkeypatch.setattr(svc_mod, "UserManagementService", lambda db: FakeUMS(db))

    service = ResidentService(db=SimpleNamespace(users=None))
    resp = await service.create_resident(_payload())
    assert resp.resident_code == "R-0001"
    assert resp.resident_email == "residente@pathsys.io"


@pytest.mark.asyncio
async def test_update_resident_success(monkeypatch):
    import app.modules.residents.services.resident_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "ResidentRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "UserManagementService", lambda db: FakeUMS(db))

    service = ResidentService(db=SimpleNamespace(users=None))
    await service.create_resident(_payload())
    updated = await service.update_resident("R-0001", ResidentUpdate(resident_name="Nuevo"))
    assert updated.resident_name == "Nuevo"