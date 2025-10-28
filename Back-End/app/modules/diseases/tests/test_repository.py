import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.modules.diseases.repositories.disease_repository import DiseaseRepository
from app.modules.diseases.models.disease import DiseaseCreate


@pytest.mark.asyncio
async def test_create_sets_timestamps_and_converts_id(mock_db, sample_disease_doc):
    repo = DiseaseRepository(mock_db)

    class _InsertResult:
        inserted_id = sample_disease_doc["_id"]

    mock_db.diseases.insert_one = AsyncMock(return_value=_InsertResult())

    payload = DiseaseCreate(
        table="CIE10",
        code="A000",
        name="CÓLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        description="CÓLERA",
        is_active=True,
    )

    created = await repo.create(payload)
    assert created.id == str(sample_disease_doc["_id"])  # conversión alias _id -> id
    assert isinstance(created.created_at, datetime)
    assert created.created_at.tzinfo is not None
    assert created.updated_at.tzinfo is not None


@pytest.mark.asyncio
async def test_get_all_and_search_and_table_with_cursor(mock_db, sample_disease_doc):
    repo = DiseaseRepository(mock_db)

    class FakeCursor:
        def __init__(self, docs):
            self._docs = docs

        def skip(self, *_):
            return self

        def limit(self, *_):
            return self

        async def to_list(self, length):
            return self._docs[:length]

    docs = [dict(sample_disease_doc)]

    # get_all
    mock_db.diseases.find = lambda *_args, **_kwargs: FakeCursor(docs)
    res_all = await repo.get_all(skip=0, limit=10, is_active=True)
    assert len(res_all) == 1
    assert res_all[0].id == str(sample_disease_doc["_id"])

    # search_by_name
    mock_db.diseases.find = lambda *_args, **_kwargs: FakeCursor(docs)
    res_name = await repo.search_by_name("COLERA", skip=0, limit=10)
    assert len(res_name) == 1

    # search_by_code
    mock_db.diseases.find = lambda *_args, **_kwargs: FakeCursor(docs)
    res_code = await repo.search_by_code("A00", skip=0, limit=10)
    assert len(res_code) == 1

    # get_by_table
    mock_db.diseases.find = lambda *_args, **_kwargs: FakeCursor(docs)
    res_table = await repo.get_by_table("CIE10", skip=0, limit=10)
    assert len(res_table) == 1


@pytest.mark.asyncio
async def test_get_by_code_delete_and_exists(mock_db, sample_disease_doc):
    repo = DiseaseRepository(mock_db)

    # get_by_code found
    mock_db.diseases.find_one = AsyncMock(return_value=sample_disease_doc)
    got = await repo.get_by_code("A000")
    assert got is not None and got.id == str(sample_disease_doc["_id"])

    # get_by_code none
    mock_db.diseases.find_one = AsyncMock(return_value=None)
    none = await repo.get_by_code("NOPE")
    assert none is None

    # delete
    class _Del:
        def __init__(self, n):
            self.deleted_count = n

    mock_db.diseases.delete_one = AsyncMock(return_value=_Del(1))
    ok = await repo.delete("507f1f77bcf86cd799439011")
    assert ok is True
    mock_db.diseases.delete_one = AsyncMock(return_value=_Del(0))
    not_ok = await repo.delete("507f1f77bcf86cd799439099")
    assert not_ok is False

    # exists_by_code
    mock_db.diseases.count_documents = AsyncMock(return_value=2)
    assert await repo.exists_by_code("A000") is True
    mock_db.diseases.count_documents = AsyncMock(return_value=0)
    assert await repo.exists_by_code("A999") is False