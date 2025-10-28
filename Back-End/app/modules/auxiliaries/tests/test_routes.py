from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.auxiliaries.routes.auxiliar_routes import router, get_auxiliar_service
from app.modules.auxiliaries.services.auxiliar_service import AuxiliarService
from app.modules.auxiliaries.schemas.auxiliar import AuxiliarCreate, AuxiliarUpdate, AuxiliarResponse, AuxiliarSearch
from app.core.exceptions import NotFoundError, ConflictError


class FakeService(AuxiliarService):
    def __init__(self):
        self._by_code = {}

    async def create_auxiliar(self, payload: AuxiliarCreate) -> AuxiliarResponse:
        if payload.auxiliar_code in self._by_code:
            raise ConflictError("Auxiliar code already exists")
        for d in self._by_code.values():
            if d.auxiliar_email == payload.auxiliar_email:
                raise ConflictError("Email already exists")
        now = datetime.now(timezone.utc)
        doc = AuxiliarResponse(
            id=str(len(self._by_code)+1),
            auxiliar_code=payload.auxiliar_code,
            auxiliar_name=payload.auxiliar_name,
            auxiliar_email=payload.auxiliar_email,
            is_active=payload.is_active,
            observations=payload.observations,
            created_at=now,
            updated_at=now,
        )
        self._by_code[doc.auxiliar_code] = doc
        return doc

    async def list_auxiliaries(self, skip=0, limit=10):
        items = list(self._by_code.values())
        return items[skip: skip + limit]

    async def search_auxiliaries(self, search_params: AuxiliarSearch, skip=0, limit=100):
        items = list(self._by_code.values())
        if search_params.q:
            q = search_params.q.lower()
            items = [d for d in items if q in d.auxiliar_name.lower() or q in d.auxiliar_code.lower() or q in d.auxiliar_email.lower()]
        return items[skip: skip + limit]

    async def get_auxiliar(self, code: str) -> AuxiliarResponse:
        d = self._by_code.get(code)
        if not d:
            raise NotFoundError("No encontrado")
        return d

    async def update_auxiliar(self, code: str, payload: AuxiliarUpdate) -> AuxiliarResponse:
        d = self._by_code.get(code)
        if not d:
            raise NotFoundError("No encontrado")
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(d, k, v)
        return d

    async def delete_auxiliar(self, code: str):
        d = self._by_code.pop(code, None)
        if not d:
            raise NotFoundError("No encontrado")
        return {"deleted": True, "auxiliar_code": code}


def create_app():
    app = FastAPI()
    service = FakeService()
    app.dependency_overrides[get_auxiliar_service] = lambda: service
    app.include_router(router, prefix="/auxiliaries")
    return app


def _payload():
    # Campos en inglés con valores en español
    return AuxiliarCreate(
        auxiliar_code="AUX-900",
        auxiliar_name="Auxiliar de Facturación",
        auxiliar_email="auxiliar.fac@example.com",
        is_active=True,
        observations="Nota de prueba",
        password="secreta123",
    )


def test_routes_crud_and_search():
    app = create_app()
    client = TestClient(app)

    # Create
    r = client.post("/auxiliaries/", json=_payload().model_dump())
    assert r.status_code == 201
    code = r.json()["auxiliar_code"]

    # List
    lst = client.get("/auxiliaries/?skip=0&limit=10")
    assert lst.status_code == 200 and isinstance(lst.json(), list) and len(lst.json()) == 1

    # Search
    srch = client.get("/auxiliaries/search", params={"q": "Auxiliar"})
    assert srch.status_code == 200 and len(srch.json()) == 1

    # Get by code
    one = client.get(f"/auxiliaries/{code}")
    assert one.status_code == 200 and one.json()["auxiliar_code"] == code

    # Update
    upd = client.put(f"/auxiliaries/{code}", json=AuxiliarUpdate(auxiliar_name="Actualizado").model_dump(exclude_unset=True))
    assert upd.status_code == 200 and upd.json()["auxiliar_name"] == "Actualizado"

    # Delete
    d = client.delete(f"/auxiliaries/{code}")
    assert d.status_code == 200 and d.json().get("deleted") is True

    # Not found after delete
    nf = client.get(f"/auxiliaries/{code}")
    assert nf.status_code == 404