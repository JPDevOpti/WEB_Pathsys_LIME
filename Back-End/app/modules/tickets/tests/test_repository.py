import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.modules.tickets.repositories.ticket_repository import TicketRepository
from app.modules.tickets.schemas.ticket import TicketSearch, TicketUpdate


@pytest.mark.asyncio
async def test_create_sets_timestamps_and_returns_model(mock_db, sample_ticket_doc):
    repo = TicketRepository(mock_db)

    class _InsertResult:
        inserted_id = sample_ticket_doc["_id"]

    mock_db.tickets.insert_one = AsyncMock(return_value=_InsertResult())
    mock_db.tickets.find_one = AsyncMock(return_value=sample_ticket_doc)

    payload = {
        "title": "Fallo en carga de imágenes",
        "category": "technical",
        "description": "No se pueden cargar imágenes en el formulario",
        "image": None,
    }

    created = await repo.create(payload)
    assert created.id == str(sample_ticket_doc["_id"])  # conversión alias _id -> id
    assert isinstance(created.created_at, datetime)
    assert created.created_at.tzinfo is not None
    assert created.updated_at.tzinfo is not None


@pytest.mark.asyncio
async def test_get_by_and_update_and_delete_by_ticket_code(mock_db, sample_ticket_doc):
    repo = TicketRepository(mock_db)

    # get_by_ticket_code
    mock_db.tickets.find_one = AsyncMock(return_value=sample_ticket_doc)
    got = await repo.get_by_ticket_code("T-2025-001")
    assert got and got.ticket_code == sample_ticket_doc["ticket_code"]

    # update_by_ticket_code
    updated_doc = dict(sample_ticket_doc)
    updated_doc["title"] = "Actualizado: problema de imágenes"
    mock_db.tickets.find_one_and_update = AsyncMock(return_value=updated_doc)
    upd = await repo.update_by_ticket_code("T-2025-001", TicketUpdate(title="Actualizado: problema de imágenes"))
    assert upd and upd.title.startswith("Actualizado")

    # delete_by_ticket_code
    class _Del:
        def __init__(self, n):
            self.deleted_count = n

    mock_db.tickets.delete_one = AsyncMock(return_value=_Del(1))
    ok = await repo.delete_by_ticket_code("T-2025-001")
    assert ok is True
    mock_db.tickets.delete_one = AsyncMock(return_value=_Del(0))
    not_ok = await repo.delete_by_ticket_code("T-2025-002")
    assert not_ok is False


@pytest.mark.asyncio
async def test_search_count_user_and_list_all_with_cursor(mock_db, sample_ticket_doc):
    repo = TicketRepository(mock_db)

    class FakeCursor:
        def __init__(self, docs):
            self._docs = docs

        def sort(self, *_args, **_kwargs):
            return self

        def skip(self, *_):
            return self

        def limit(self, *_):
            return self

        async def to_list(self, length):
            return self._docs[:length]

    docs = [dict(sample_ticket_doc)]

    # search_tickets
    mock_db.tickets.find = lambda *_args, **_kwargs: FakeCursor(docs)
    res_search = await repo.search_tickets(TicketSearch(search_text="imágenes"), skip=0, limit=10)
    assert len(res_search) == 1 and res_search[0].ticket_code == sample_ticket_doc["ticket_code"]

    # count_tickets
    mock_db.tickets.count_documents = AsyncMock(return_value=5)
    total = await repo.count_tickets(TicketSearch(search_text="imágenes"))
    assert total == 5

    # get_tickets_by_user
    mock_db.tickets.find = lambda *_args, **_kwargs: FakeCursor(docs)
    by_user = await repo.get_tickets_by_user("user-123", skip=0, limit=10)
    assert len(by_user) == 1 and by_user[0].created_by == "user-123"

    # list_all_tickets
    mock_db.tickets.find = lambda *_args, **_kwargs: FakeCursor(docs)
    all_tk = await repo.list_all_tickets(skip=0, limit=10)
    assert len(all_tk) == 1 and all_tk[0].ticket_code == sample_ticket_doc["ticket_code"]


@pytest.mark.asyncio
async def test_initialize_indexes(mock_db):
    repo = TicketRepository(mock_db)
    mock_db.tickets.create_index = AsyncMock()
    await repo.initialize_indexes()
    assert mock_db.tickets.create_index.await_count >= 4