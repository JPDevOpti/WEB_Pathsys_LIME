import pytest
from datetime import datetime, timezone

from app.modules.auxiliaries.services.auxiliar_service import AuxiliarService
from app.modules.auxiliaries.schemas.auxiliar import AuxiliarCreate, AuxiliarUpdate, AuxiliarSearch
from app.core.exceptions import NotFoundError, ConflictError


class FakeRepo:
    def __init__(self):
        self._by_code = {}

    async def get_by_auxiliar_code(self, code):
        return self._by_code.get(code)

    async def get_by_email(self, email):
        for d in self._by_code.values():
            if d["auxiliar_email"] == email:
                return d
        return None

    async def create(self, payload: AuxiliarCreate):
        now = datetime.now(timezone.utc)
        if await self.get_by_auxiliar_code(payload.auxiliar_code):
            raise ConflictError("Auxiliar code already exists")
        if await self.get_by_email(payload.auxiliar_email):
            raise ConflictError("Email already exists")
        doc = {
            "id": f"{len(self._by_code)+1}",
            "auxiliar_code": payload.auxiliar_code,
            "auxiliar_name": payload.auxiliar_name,
            "auxiliar_email": payload.auxiliar_email,
            "is_active": payload.is_active,
            "observations": payload.observations,
            "created_at": now,
            "updated_at": now,
        }
        self._by_code[payload.auxiliar_code] = doc
        return doc

    async def list_active(self, skip=0, limit=100):
        items = [d for d in self._by_code.values() if d["is_active"]]
        return items[skip: skip + limit]

    async def search(self, search_params: AuxiliarSearch, skip=0, limit=100):
        items = list(self._by_code.values())
        def match(d):
            if search_params.q:
                q = search_params.q.lower()
                if q in d["auxiliar_name"].lower() or q in d["auxiliar_code"].lower() or q in d["auxiliar_email"].lower():
                    pass
                else:
                    return False
            if search_params.auxiliar_name and search_params.auxiliar_name.lower() not in d["auxiliar_name"].lower():
                return False
            if search_params.auxiliar_code and search_params.auxiliar_code != d["auxiliar_code"]:
                return False
            if search_params.auxiliar_email and search_params.auxiliar_email.lower() not in d["auxiliar_email"].lower():
                return False
            if search_params.is_active is not None and search_params.is_active != d["is_active"]:
                return False
            return True
        items = [d for d in items if match(d)]
        return items[skip: skip + limit]

    async def update_by_auxiliar_code(self, code, update_data):
        d = self._by_code.get(code)
        if not d:
            return None
        d.update(update_data)
        d["updated_at"] = datetime.now(timezone.utc)
        return d

    async def delete_by_auxiliar_code(self, code):
        return self._by_code.pop(code, None) is not None


class FakeUserService:
    def __init__(self):
        self.created = []
        self.updated = []
        self.fail_create = False
        self.fail_update = False

    async def create_user_for_auxiliar(self, name, email, password, auxiliar_code, is_active):
        if self.fail_create:
            return None
        self.created.append(email)
        return {"email": email}

    async def update_user_for_auxiliar(self, auxiliar_code, name=None, email=None, password=None, is_active=None):
        if self.fail_update:
            return None
        self.updated.append(auxiliar_code)
        return {"auxiliar_code": auxiliar_code}


class _DummyDB:
    def __init__(self):
        self.auxiliaries = object()
    def get_collection(self, name: str):
        return object()


@pytest.mark.asyncio
async def test_create_get_list_search_update_delete():
    svc = AuxiliarService(_DummyDB())
    svc.repo = FakeRepo()
    svc.user_service = FakeUserService()

    payload = AuxiliarCreate(
        auxiliar_code="AUX-100",
        auxiliar_name="Auxiliar Inicial",
        auxiliar_email="auxiliar.inicial@example.com",
        is_active=True,
        observations="Nota",
        password="secreta123",
    )
    created = await svc.create_auxiliar(payload)
    assert created.auxiliar_code == "AUX-100" and created.auxiliar_name.startswith("Auxiliar")

    with pytest.raises(ConflictError):
        await svc.create_auxiliar(AuxiliarCreate(
            auxiliar_code="AUX-100",
            auxiliar_name="Dup",
            auxiliar_email="dup@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))
    with pytest.raises(ConflictError):
        await svc.create_auxiliar(AuxiliarCreate(
            auxiliar_code="AUX-101",
            auxiliar_name="Dup",
            auxiliar_email="auxiliar.inicial@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))

    got = await svc.get_auxiliar("AUX-100")
    assert got.auxiliar_email == "auxiliar.inicial@example.com"

    lst = await svc.list_auxiliaries()
    assert len(lst) == 1
    srch = await svc.search_auxiliaries(AuxiliarSearch(q="Auxiliar"))
    assert len(srch) == 1

    upd = await svc.update_auxiliar("AUX-100", AuxiliarUpdate(auxiliar_name="Actualizado"))
    assert upd.auxiliar_name == "Actualizado"

    res = await svc.delete_auxiliar("AUX-100")
    assert res["deleted"] is True
    with pytest.raises(NotFoundError):
        await svc.get_auxiliar("AUX-100")


@pytest.mark.asyncio
async def test_create_user_failure_rolls_back():
    svc = AuxiliarService(_DummyDB())
    svc.repo = FakeRepo()
    fake_users = FakeUserService()
    fake_users.fail_create = True
    svc.user_service = fake_users

    with pytest.raises(ConflictError):
        await svc.create_auxiliar(AuxiliarCreate(
            auxiliar_code="AUX-200",
            auxiliar_name="Falla Usuario",
            auxiliar_email="falla@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))