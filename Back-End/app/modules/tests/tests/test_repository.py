import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.modules.tests.repositories.test_repository import TestRepository
from app.modules.tests.schemas.test import TestCreate, TestSearch, TestUpdate


@pytest.mark.asyncio
async def test_create_sets_timestamps_and_converts_id(mock_db, sample_test_doc):
    repo = TestRepository(mock_db)

    class _InsertResult:
        inserted_id = sample_test_doc["_id"]

    mock_db.tests.insert_one = AsyncMock(return_value=_InsertResult())
    mock_db.tests.find_one = AsyncMock(return_value=sample_test_doc)

    payload = TestCreate(
        name="Hematología básica",
        test_code="hb-01",
        description="Perfil sanguíneo estándar",
        time=30,
        price=25.5,
        is_active=True,
    )

    created = await repo.create(payload)
    assert created["id"] == str(sample_test_doc["_id"])  # conversión en _convert
    assert isinstance(created.get("created_at"), datetime)
    assert created["created_at"].tzinfo is not None
    assert created["updated_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_update_by_code_sets_updated_at(mock_db, sample_test_doc):
    repo = TestRepository(mock_db)

    # Simular que existe el documento
    mock_db.tests.find_one = AsyncMock(side_effect=[sample_test_doc, sample_test_doc])

    class _UpdateResult:
        modified_count = 1

    mock_db.tests.update_one = AsyncMock(return_value=_UpdateResult())

    out = await repo.update_by_code("HB-01", TestUpdate(description="Descripción actualizada"))
    assert out is not None
    assert out["updated_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_list_active_and_all_with_chained_cursor(mock_db, sample_test_doc):
    repo = TestRepository(mock_db)

    class FakeCursor:
        def __init__(self, docs):
            self._docs = docs

        def skip(self, *_):
            return self

        def limit(self, *_):
            return self

        def sort(self, *_):
            return self

        async def to_list(self, length):
            return self._docs[:length]

    docs = [dict(sample_test_doc)]
    mock_db.tests.find = lambda *_args, **_kwargs: FakeCursor(docs)

    active = await repo.list_active(TestSearch(query=None, skip=0, limit=10))
    assert len(active) == 1
    assert active[0]["id"] == str(sample_test_doc["_id"])

    all_docs = await repo.list_all(TestSearch(query=None, skip=0, limit=10))
    assert len(all_docs) == 1
    assert all_docs[0]["id"] == str(sample_test_doc["_id"])