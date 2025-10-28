import pytest
from types import SimpleNamespace
from datetime import datetime, timezone
from app.modules.cases.services.case_service import CaseService
from app.modules.cases.schemas.case import CaseCreate, PatientInfo, EntityInfo, CaseUpdate


class FakeRepo:
    def __init__(self, db):
        self.collection = SimpleNamespace()
        self._store = {}

    async def create(self, data):
        data = dict(data)
        data["_id"] = "656565656565656565656565"
        data.setdefault("created_at", datetime.now(timezone.utc))
        data.setdefault("updated_at", datetime.now(timezone.utc))
        self._store[data["case_code"]] = data
        return data

    async def get_by_case_code(self, code):
        return self._store.get(code)

    async def update_by_case_code(self, code, update):
        self._store[code] = {**self._store.get(code, {}), **update}
        return self._store[code]

    async def delete_by_case_code(self, code):
        return bool(self._store.pop(code, None))


class FakeSeq:
    def __init__(self, fixed_code="2025-00001"):
        self.fixed_code = fixed_code

    async def generate_case_code(self, year):
        return self.fixed_code


def _payload_with_patient(patient_code=None):
    info = {
        "patient_code": patient_code or "",
        "identification_type": 1,
        "identification_number": "12345678",
        "name": "Juan Pérez",
        "age": 35,
        "gender": "Masculino",
        "entity_info": EntityInfo(id="ENT-1", name="Entidad Demo"),
        "care_type": "Ambulatorio",
        "observations": None,
    }
    return CaseCreate(
        patient_info=PatientInfo(**info),
        requesting_physician="Dr. Demo",
        service="Consulta externa",
        samples=[],
        observations=None,
    )


@pytest.mark.asyncio
async def test_create_case_derives_patient_code(monkeypatch):
    # Monkeypatch repos
    import app.modules.cases.services.case_service as svc_mod
    monkeypatch.setattr(svc_mod, "CaseRepository", lambda db: FakeRepo(db))
    monkeypatch.setattr(svc_mod, "CaseConsecutiveRepository", lambda db: FakeSeq("2025-00077"))

    service = CaseService(db=SimpleNamespace(users=None))

    payload = _payload_with_patient(patient_code=None)
    resp = await service.create_case(payload)
    assert resp.case_code == "2025-00077"
    assert resp.patient_info.patient_code == "1-12345678"


@pytest.mark.asyncio
async def test_update_case_to_completed_invalid_flow_raises(monkeypatch):
    import app.modules.cases.services.case_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "CaseRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "CaseConsecutiveRepository", lambda db: FakeSeq("2025-00001"))

    service = CaseService(db=SimpleNamespace(users=None))

    # Crear caso en estado por defecto "En proceso"
    created = await service.create_case(_payload_with_patient())
    # Intentar marcar como Completado desde En proceso
    with pytest.raises(Exception) as exc:
        await service.update_case(created.case_code, CaseUpdate(state="Completado"))
    assert "Solo se pueden completar casos en estado 'Por entregar'" in str(exc.value)


@pytest.mark.asyncio
async def test_delete_case_success(monkeypatch):
    import app.modules.cases.services.case_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "CaseRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "CaseConsecutiveRepository", lambda db: FakeSeq("2025-00001"))

    service = CaseService(db=SimpleNamespace(users=None))
    created = await service.create_case(_payload_with_patient())
    out = await service.delete_case(created.case_code)
    assert out["deleted"] is True
    assert out["case_code"] == created.case_code


@pytest.mark.asyncio
async def test_get_case_not_found(monkeypatch):
    import app.modules.cases.services.case_service as svc_mod
    repo = FakeRepo(SimpleNamespace())
    monkeypatch.setattr(svc_mod, "CaseRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "CaseConsecutiveRepository", lambda db: FakeSeq("2025-00001"))

    service = CaseService(db=SimpleNamespace(users=None))
    with pytest.raises(Exception):
        await service.get_case("NO-EXISTE")


@pytest.mark.asyncio
async def test_list_cases_default_pathologist_filter(monkeypatch, mock_db, sample_case_doc):
    import app.modules.cases.services.case_service as svc_mod

    class RepoWithFind(FakeRepo):
        def __init__(self, db):
            super().__init__(db)
            self.collection = SimpleNamespace()
            self.last_filters = None

            def _find(filters):
                self.last_filters = filters
                class _Cursor:
                    def __init__(self, docs):
                        self._docs = docs
                    def sort(self, *_a, **_k):
                        return self
                    def skip(self, *_a, **_k):
                        return self
                    def limit(self, *_a, **_k):
                        return self
                    async def to_list(self, length=None):
                        return self._docs[: length or len(self._docs)]
                return _Cursor([sample_case_doc])

            self.collection.find = _find

    repo = RepoWithFind(mock_db)
    monkeypatch.setattr(svc_mod, "CaseRepository", lambda db: repo)
    monkeypatch.setattr(svc_mod, "CaseConsecutiveRepository", lambda db: FakeSeq("2025-00001"))

    # Simula usuario patólogo autenticado sin filtro explícito de pathologist
    from unittest.mock import AsyncMock
    mock_db.users.find_one = AsyncMock(return_value={"_id": "507f1f77bcf86cd799439011", "role": "pathologist", "pathologist_code": "P-1", "is_active": True})

    service = CaseService(db=mock_db)
    cases = await service.list_cases(current_user_id="507f1f77bcf86cd799439011")
    assert isinstance(cases, list)
    assert repo.last_filters is not None
    # Debe aplicar filtro por assigned_pathologist.id cuando el usuario es patólogo
    assert repo.last_filters.get("assigned_pathologist.id") == "P-1"