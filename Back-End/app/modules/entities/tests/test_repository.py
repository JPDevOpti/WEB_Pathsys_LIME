import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.modules.entities.repositories.entity_repository import EntityRepository
from app.modules.entities.schemas.entity import EntityCreate, EntitySearch, EntityUpdate


@pytest.mark.asyncio
async def test_create_sets_timestamps_and_converts_id(mock_db, sample_entity_doc):
    repo = EntityRepository(mock_db)

    class _InsertResult:
        inserted_id = sample_entity_doc["_id"]

    mock_db.entities.insert_one = AsyncMock(return_value=_InsertResult())
    mock_db.entities.find_one = AsyncMock(return_value=sample_entity_doc)

    payload = EntityCreate(
        name="Laboratorio Central",
        entity_code="en-01",
        notes="Entidad de referencia",
        is_active=True,
    )

    created = await repo.create(payload)
    assert created["id"] == str(sample_entity_doc["_id"])  # conversión en _convert
    assert isinstance(created.get("created_at"), datetime)
    assert created["created_at"].tzinfo is not None
    assert created["updated_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_update_by_code_sets_updated_at(mock_db, sample_entity_doc):
    repo = EntityRepository(mock_db)

    # Simula existencia y retorno actualizado
    mock_db.entities.find_one = AsyncMock(side_effect=[sample_entity_doc, sample_entity_doc])

    class _UpdateResult:
        modified_count = 1

    mock_db.entities.update_one = AsyncMock(return_value=_UpdateResult())

    out = await repo.update_by_code("EN-01", EntityUpdate(notes="Actualizada"))
    assert out is not None
    assert out["updated_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_list_active_and_all_with_cursor(mock_db, sample_entity_doc):
    repo = EntityRepository(mock_db)

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

    docs = [dict(sample_entity_doc)]
    mock_db.entities.find = lambda *_args, **_kwargs: FakeCursor(docs)

    active = await repo.list_active(EntitySearch(query=None, skip=0, limit=10))
    assert len(active) == 1
    assert active[0]["id"] == str(sample_entity_doc["_id"])

    all_docs = await repo.list_all(EntitySearch(query=None, skip=0, limit=10))
    assert len(all_docs) == 1
    assert all_docs[0]["id"] == str(sample_entity_doc["_id"])