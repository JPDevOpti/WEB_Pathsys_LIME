import pytest
from datetime import datetime, timezone

from app.modules.billing.services.billing_service import BillingService
from app.modules.billing.schemas.billing import BillingCreate, BillingUpdate, BillingSearch
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


class FakeRepo:
    def __init__(self):
        self._by_code = {}

    async def get_by_billing_code(self, code):
        return self._by_code.get(code)

    async def get_by_email(self, email):
        for d in self._by_code.values():
            if d["billing_email"] == email:
                return d
        return None

    async def create(self, payload: BillingCreate):
        now = datetime.now(timezone.utc)
        if await self.get_by_billing_code(payload.billing_code):
            raise ConflictError("Billing code already exists")
        if await self.get_by_email(payload.billing_email):
            raise ConflictError("Email already exists")
        doc = {
            "id": f"{len(self._by_code)+1}",
            "billing_code": payload.billing_code,
            "billing_name": payload.billing_name,
            "billing_email": payload.billing_email,
            "is_active": payload.is_active,
            "observations": payload.observations,
            "created_at": now,
            "updated_at": now,
        }
        self._by_code[payload.billing_code] = doc
        return doc

    async def list_active(self, skip=0, limit=100):
        items = [d for d in self._by_code.values() if d["is_active"]]
        return items[skip: skip + limit]

    async def search(self, search_params: BillingSearch, skip=0, limit=100):
        items = list(self._by_code.values())
        def match(d):
            if search_params.q:
                q = search_params.q.lower()
                if q in d["billing_name"].lower() or q in d["billing_code"].lower() or q in d["billing_email"].lower():
                    pass
                else:
                    return False
            if search_params.billing_name and search_params.billing_name.lower() not in d["billing_name"].lower():
                return False
            if search_params.billing_code and search_params.billing_code != d["billing_code"]:
                return False
            if search_params.billing_email and search_params.billing_email.lower() not in d["billing_email"].lower():
                return False
            if search_params.is_active is not None and search_params.is_active != d["is_active"]:
                return False
            return True
        items = [d for d in items if match(d)]
        return items[skip: skip + limit]

    async def update_by_billing_code(self, code, update_data):
        d = self._by_code.get(code)
        if not d:
            return None
        d.update(update_data)
        d["updated_at"] = datetime.now(timezone.utc)
        return d

    async def delete_by_billing_code(self, code):
        return self._by_code.pop(code, None) is not None


class FakeUserService:
    def __init__(self):
        self.created = []
        self.updated = []
        self.fail_create = False
        self.fail_update = False

    async def create_user_for_billing(self, name, email, password, billing_code, is_active):
        if self.fail_create:
            return None
        self.created.append(email)
        return {"email": email}

    async def update_user_for_billing(self, billing_code, name=None, email=None, password=None, is_active=None):
        if self.fail_update:
            return None
        self.updated.append(billing_code)
        return {"billing_code": billing_code}


class _DummyDB:
    def __init__(self):
        # Atributos mínimos para inicialización de repos y servicios reales
        self.billing = object()
    
    def get_collection(self, name: str):
        # Devuelve un objeto ficticio; no será usado porque se sobreescriben dependencias
        return object()


@pytest.mark.asyncio
async def test_create_get_list_search_update_delete():
    svc = BillingService(_DummyDB())
    svc.repo = FakeRepo()
    svc.user_service = FakeUserService()

    # Crear
    payload = BillingCreate(
        billing_code="FAC-100",
        billing_name="Usuario Inicial",
        billing_email="usuario.inicial@example.com",
        is_active=True,
        observations="Nota",
        password="secreta123",
    )
    created = await svc.create_billing(payload)
    assert created.billing_code == "FAC-100" and created.billing_name.startswith("Usuario")

    # Duplicados
    with pytest.raises(ConflictError):
        await svc.create_billing(BillingCreate(
            billing_code="FAC-100",
            billing_name="Dup",
            billing_email="dup@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))
    with pytest.raises(ConflictError):
        await svc.create_billing(BillingCreate(
            billing_code="FAC-101",
            billing_name="Dup",
            billing_email="usuario.inicial@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))

    # Obtener
    got = await svc.get_billing("FAC-100")
    assert got.billing_email == "usuario.inicial@example.com"

    # Listar y buscar
    lst = await svc.list_billing()
    assert len(lst) == 1
    srch = await svc.search_billing(BillingSearch(q="Usuario"))
    assert len(srch) == 1

    # Actualizar
    upd = await svc.update_billing("FAC-100", BillingUpdate(billing_name="Actualizado"))
    assert upd.billing_name == "Actualizado"

    # Eliminar
    res = await svc.delete_billing("FAC-100")
    assert res["deleted"] is True
    with pytest.raises(NotFoundError):
        await svc.get_billing("FAC-100")


@pytest.mark.asyncio
async def test_create_user_failure_rolls_back():
    svc = BillingService(_DummyDB())
    svc.repo = FakeRepo()
    fake_users = FakeUserService()
    fake_users.fail_create = True
    svc.user_service = fake_users

    with pytest.raises(ConflictError):
        await svc.create_billing(BillingCreate(
            billing_code="FAC-200",
            billing_name="Falla Usuario",
            billing_email="falla@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))