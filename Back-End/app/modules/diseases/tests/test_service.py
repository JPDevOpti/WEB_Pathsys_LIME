import pytest
from datetime import datetime, timezone

from app.modules.diseases.services.disease_service import DiseaseService
from app.modules.diseases.models.disease import DiseaseCreate, DiseaseResponse


class FakeRepo:
    def __init__(self):
        self._store = {}

    async def get_by_code(self, code: str):
        return self._store.get(code.upper())

    async def create(self, disease: DiseaseCreate):
        code = disease.code.upper()
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

    async def get_all(self, skip: int, limit: int, is_active=None):
        data = list(self._store.values())
        if is_active is not None:
            data = [d for d in data if d.is_active == is_active]
        return data[skip: skip + limit]

    async def count_total(self, is_active=None):
        if is_active is None:
            return len(self._store)
        return sum(1 for d in self._store.values() if d.is_active == is_active)

    async def search_by_name(self, name: str, skip: int, limit: int):
        data = [d for d in self._store.values() if name.lower() in d.name.lower()]
        return data[skip: skip + limit]

    async def search_by_code(self, code: str, skip: int, limit: int):
        data = [d for d in self._store.values() if code.lower() in d.code.lower()]
        return data[skip: skip + limit]

    async def get_by_table(self, table: str, skip: int, limit: int):
        data = [d for d in self._store.values() if d.table == table]
        return data[skip: skip + limit]

    async def delete(self, disease_id: str) -> bool:
        # simple delete by matching any stored id
        for code, d in list(self._store.items()):
            if d.id == disease_id:
                self._store.pop(code)
                return True
        return False


def _payload(code="A000"):
    # Campos en inglés, valores en español
    return DiseaseCreate(
        table="CIE10",
        code=code,
        name="CÓLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        description="CÓLERA",
        is_active=True,
    )


@pytest.mark.asyncio
async def test_create_success_then_conflict():
    repo = FakeRepo()
    service = DiseaseService(repository=repo)

    created = await service.create_disease(_payload("A000"))
    assert created.code == "A000"

    with pytest.raises(Exception) as ei:
        await service.create_disease(_payload("A000"))
    assert getattr(ei.value, "status_code", 0) == 400


@pytest.mark.asyncio
async def test_get_all_search_table_get_and_delete_flow():
    repo = FakeRepo()
    service = DiseaseService(repository=repo)

    # no existe al inicio
    not_found = await service.get_disease_by_code("A001")
    assert not_found is None

    # crea dos enfermedades
    await service.create_disease(_payload("A000"))
    await service.create_disease(_payload("A001"))

    # listado (por defecto sólo activas)
    lst = await service.get_all_diseases(skip=0, limit=10)
    assert lst["total"] == 2 and len(lst["diseases"]) == 2

    # búsqueda por nombre
    by_name = await service.search_diseases_by_name("CÓLERA", 0, 10)
    assert len(by_name["diseases"]) == 2

    # búsqueda por código
    by_code = await service.search_diseases_by_code("A00", 0, 10)
    assert len(by_code["diseases"]) == 2

    # por tabla
    by_table = await service.get_diseases_by_table("CIE10", 0, 10)
    assert len(by_table["diseases"]) == 2

    # get por código
    got = await service.get_disease_by_code("A000")
    assert got and got.code == "A000"

    # delete
    # busca id del primero
    disease_id = got.id
    ok = await service.delete_disease(disease_id)
    assert ok is True

    with pytest.raises(Exception) as ei2:
        await service.delete_disease("507f1f77bcf86cd799439099")
    assert getattr(ei2.value, "status_code", 0) == 404