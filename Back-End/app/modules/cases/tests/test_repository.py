import pytest
from unittest.mock import AsyncMock
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.repositories.urgent_cases_repository import UrgentCasesRepository


@pytest.mark.asyncio
async def test_case_repository_update_sets_updated_at(mock_db):
    repo = CaseRepository(mock_db)
    mock_db.cases.update_one = AsyncMock()
    mock_db.cases.find_one = AsyncMock(return_value={"case_code": "2025-00001", "updated_at": object()})

    await repo.update_by_case_code("2025-00001", {"state": "Por firmar"})
    # Verifica que $set incluye updated_at
    args, kwargs = mock_db.cases.update_one.call_args
    assert args[0] == {"case_code": "2025-00001"}
    set_doc = args[1]["$set"]
    assert set_doc["state"] == "Por firmar"
    assert "updated_at" in set_doc


@pytest.mark.asyncio
async def test_case_repository_delete_returns_bool(mock_db):
    repo = CaseRepository(mock_db)
    mock_db.cases.delete_one = AsyncMock(return_value=type("R", (), {"deleted_count": 1}))
    ok = await repo.delete_by_case_code("2025-00001")
    assert ok is True


@pytest.mark.asyncio
async def test_urgent_cases_repository_builds_pipeline_with_pathologist_filter(mock_db):
    repo = UrgentCasesRepository(mock_db)

    class Agg:
        def __init__(self, pipeline):
            self.pipeline = pipeline

        async def to_list(self, length):
            return []

    captured = {}

    def fake_aggregate(pipeline):
        captured["pipeline"] = pipeline
        return Agg(pipeline)

    mock_db.cases.aggregate = fake_aggregate  # type: ignore

    await repo.find_urgent_cases(limit=10, min_days=7, pathologist_code="P-9")
    pipeline = captured["pipeline"]
    # Verifica que se construye filtro de estado por $in
    assert pipeline[0]["$match"]["state"]["$in"] == ["En proceso", "Por firmar"]
    # Asegura que se filtre por patólogo si se proporciona
    assert pipeline[0]["$match"]["assigned_pathologist.id"] == "P-9"