from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.billing.routes.billing_routes import router, get_billing_service
from app.modules.billing.services.billing_service import BillingService
from app.modules.billing.schemas.billing import BillingCreate, BillingUpdate, BillingResponse, BillingSearch
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


class FakeService(BillingService):
    def __init__(self):
        self._by_code = {}

    async def create_billing(self, payload: BillingCreate) -> BillingResponse:
        if payload.billing_code in self._by_code:
            raise ConflictError("Billing code already exists")
        for d in self._by_code.values():
            if d.billing_email == payload.billing_email:
                raise ConflictError("Email already exists")
        now = datetime.now(timezone.utc)
        doc = BillingResponse(
            id=str(len(self._by_code)+1),
            billing_code=payload.billing_code,
            billing_name=payload.billing_name,
            billing_email=payload.billing_email,
            is_active=payload.is_active,
            observations=payload.observations,
            created_at=now,
            updated_at=now,
        )
        self._by_code[doc.billing_code] = doc
        return doc

    async def list_billing(self, skip=0, limit=10):
        items = list(self._by_code.values())
        return items[skip: skip + limit]

    async def search_billing(self, search_params: BillingSearch, skip=0, limit=100):
        items = list(self._by_code.values())
        if search_params.q:
            q = search_params.q.lower()
            items = [d for d in items if q in d.billing_name.lower() or q in d.billing_code.lower() or q in d.billing_email.lower()]
        return items[skip: skip + limit]

    async def get_billing(self, code: str) -> BillingResponse:
        d = self._by_code.get(code)
        if not d:
            raise NotFoundError("No encontrado")
        return d

    async def update_billing(self, code: str, payload: BillingUpdate) -> BillingResponse:
        d = self._by_code.get(code)
        if not d:
            raise NotFoundError("No encontrado")
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(d, k, v)
        return d

    async def delete_billing(self, code: str):
        d = self._by_code.pop(code, None)
        if not d:
            raise NotFoundError("No encontrado")
        return {"deleted": True, "billing_code": code}


def create_app():
    app = FastAPI()
    service = FakeService()
    app.dependency_overrides[get_billing_service] = lambda: service
    app.include_router(router, prefix="/billing")
    return app


def _payload():
    # Campos en inglés con valores en español
    return BillingCreate(
        billing_code="FAC-900",
        billing_name="Usuario de Facturación",
        billing_email="usuario.fac@example.com",
        is_active=True,
        observations="Nota de prueba",
        password="secreta123",
    )


def test_routes_crud_and_search():
    app = create_app()
    client = TestClient(app)

    # Create
    r = client.post("/billing/", json=_payload().model_dump())
    assert r.status_code == 201
    code = r.json()["billing_code"]

    # List
    lst = client.get("/billing/?skip=0&limit=10")
    assert lst.status_code == 200 and isinstance(lst.json(), list) and len(lst.json()) == 1

    # Search
    srch = client.get("/billing/search", params={"q": "Usuario"})
    assert srch.status_code == 200 and len(srch.json()) == 1

    # Get by code
    one = client.get(f"/billing/{code}")
    assert one.status_code == 200 and one.json()["billing_code"] == code

    # Update
    upd = client.put(f"/billing/{code}", json=BillingUpdate(billing_name="Actualizado").model_dump(exclude_unset=True))
    assert upd.status_code == 200 and upd.json()["billing_name"] == "Actualizado"

    # Delete
    d = client.delete(f"/billing/{code}")
    assert d.status_code == 200 and d.json().get("deleted") is True

    # Not found after delete
    nf = client.get(f"/billing/{code}")
    assert nf.status_code == 404