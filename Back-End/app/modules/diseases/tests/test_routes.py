from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.diseases.routes.disease_routes import router, get_disease_service
from app.modules.diseases.services.disease_service import DiseaseService
from app.modules.diseases.models.disease import DiseaseCreate, DiseaseResponse


class FakeService(DiseaseService):
    def __init__(self):
        self._store = {}

    async def create_disease(self, disease: DiseaseCreate) -> DiseaseResponse:
        code = disease.code.upper()
        if code in self._store:
            raise HTTPException(status_code=400, detail="Código duplicado")
        doc = DiseaseResponse(
            _id="507f1f77bcf86cd799439011",
            table=disease.table,
            code=code,
            name=disease.name,
            description=disease.description,
            is_active=disease.is_active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._store[code] = doc
        return doc

    async def get_all_diseases(self, skip: int = 0, limit: int = 100, is_active=None):
        data = list(self._store.values())
        if is_active is None:
            is_active = True
        data = [d for d in data if d.is_active == is_active]
        return {
            "diseases": data[skip: skip + limit],
            "total": len(data),
            "skip": skip,
            "limit": limit,
        }

    async def search_diseases_by_name(self, name: str, skip: int = 0, limit: int = 100):
        data = [d for d in self._store.values() if name.lower() in d.name.lower()]
        return {"diseases": data[skip: skip + limit], "search_term": name, "skip": skip, "limit": limit}

    async def search_diseases_by_code(self, code: str, skip: int = 0, limit: int = 100):
        data = [d for d in self._store.values() if code.lower() in d.code.lower()]
        return {"diseases": data[skip: skip + limit], "search_term": code, "skip": skip, "limit": limit}

    async def get_diseases_by_table(self, table: str, skip: int = 0, limit: int = 100):
        data = [d for d in self._store.values() if d.table == table]
        return {"diseases": data[skip: skip + limit], "table": table, "skip": skip, "limit": limit}

    async def get_disease_by_code(self, code: str):
        code = code.upper()
        return self._store.get(code)

    async def delete_disease(self, disease_id: str) -> bool:
        for code, d in list(self._store.items()):
            if d.id == disease_id:
                self._store.pop(code)
                return True
        raise HTTPException(status_code=404, detail="No encontrada")


def create_app():
    app = FastAPI()
    # Instancia única por test
    service = FakeService()
    app.dependency_overrides[get_disease_service] = lambda: service
    app.include_router(router, prefix="/diseases")
    return app


def _payload(code="A000"):
    return DiseaseCreate(
        table="CIE10",
        code=code,
        name="CÓLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        description="CÓLERA",
        is_active=True,
    )


def test_route_create_success_and_conflict():
    app = create_app()
    client = TestClient(app)
    r1 = client.post("/diseases/", json=_payload().model_dump())
    # En rutas actuales no se establece 201, por lo que es 200
    assert r1.status_code == 200
    r2 = client.post("/diseases/", json=_payload().model_dump())
    assert r2.status_code == 400


def test_route_list_and_search_and_table():
    app = create_app()
    client = TestClient(app)
    client.post("/diseases/", json=_payload("A000").model_dump())
    client.post("/diseases/", json=_payload("A001").model_dump())

    lst = client.get("/diseases/?skip=0&limit=10")
    assert lst.status_code == 200
    body = lst.json()
    assert body["total"] == 2 and len(body["diseases"]) == 2

    by_name = client.get("/diseases/search/name?q=CÓLERA&skip=0&limit=10")
    assert by_name.status_code == 200 and len(by_name.json()["diseases"]) == 2

    by_code = client.get("/diseases/search/code?q=A00&skip=0&limit=10")
    assert by_code.status_code == 200 and len(by_code.json()["diseases"]) == 2

    by_table = client.get("/diseases/table/CIE10?skip=0&limit=10")
    assert by_table.status_code == 200 and len(by_table.json()["diseases"]) == 2


def test_route_get_not_found_and_delete():
    app = create_app()
    client = TestClient(app)
    r = client.get("/diseases/code/NOPE")
    assert r.status_code == 404

    created = client.post("/diseases/", json=_payload("A010").model_dump())
    assert created.status_code == 200
    disease_id = created.json()["id"]
    d = client.delete(f"/diseases/{disease_id}")
    assert d.status_code == 200