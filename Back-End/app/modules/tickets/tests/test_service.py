import pytest
from datetime import datetime, timezone

from app.modules.tickets.services.ticket_service import TicketService
from app.modules.tickets.models.ticket import Ticket, TicketStatusEnum, TicketCategoryEnum
from app.modules.tickets.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketSearch,
    TicketStatusUpdate,
)
from app.core.exceptions import NotFoundError, BadRequestError


class FakeTicketRepo:
    def __init__(self):
        self._by_code = {}

    async def create(self, data: dict) -> Ticket:
        now = datetime.now(timezone.utc)
        doc = Ticket(
            _id="507f1f77bcf86cd799439013",
            ticket_code=data["ticket_code"],
            title=data["title"],
            category=data["category"],
            description=data["description"],
            image=data.get("image"),
            ticket_date=now,
            status=TicketStatusEnum.OPEN,
            created_by=data["created_by"],
            created_at=now,
            updated_at=now,
        )
        self._by_code[doc.ticket_code] = doc
        return doc

    async def get_by_ticket_code(self, code: str):
        return self._by_code.get(code)

    async def update_by_ticket_code(self, code: str, update: TicketUpdate):
        t = self._by_code.get(code)
        if not t:
            return None
        data = update.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(t, k, v)
        t.updated_at = datetime.now(timezone.utc)
        return t

    async def delete_by_ticket_code(self, code: str) -> bool:
        return self._by_code.pop(code, None) is not None

    async def list_all_tickets(self, skip=0, limit=20, sort_by="ticket_date", sort_order="desc"):
        return list(self._by_code.values())[skip: skip + limit]

    async def search_tickets(self, search_params: TicketSearch, skip=0, limit=20, sort_by="ticket_date", sort_order="desc"):
        items = list(self._by_code.values())
        if search_params.search_text:
            txt = search_params.search_text.lower()
            items = [t for t in items if txt in t.title.lower() or txt in t.description.lower()]
        if search_params.status:
            items = [t for t in items if t.status == search_params.status]
        if search_params.category:
            items = [t for t in items if t.category == search_params.category]
        if search_params.created_by:
            items = [t for t in items if t.created_by == search_params.created_by]
        return items[skip: skip + limit]

    async def count_tickets(self, search_params: TicketSearch) -> int:
        return len(await self.search_tickets(search_params))

    async def get_tickets_by_user(self, user_id: str, skip=0, limit=20):
        items = [t for t in self._by_code.values() if t.created_by == user_id]
        return items[skip: skip + limit]


class FakeConsecutiveRepo:
    def __init__(self):
        self._year_to_last = {}

    async def get_next_number(self, year: int) -> int:
        last = self._year_to_last.get(year, 0) + 1
        self._year_to_last[year] = last
        return last

    async def get_next_number_preview(self, year: int) -> int:
        return self._year_to_last.get(year, 0) + 1


def _payload():
    # Campos en inglés, valores en español
    return TicketCreate(
        title="Fallo en carga de imágenes",
        category=TicketCategoryEnum.TECHNICAL,
        description="No se pueden cargar imágenes en el formulario",
        image=None,
    )


class _DummyDB:
    def __getitem__(self, name: str):
        # Devolver mocks para evitar fallo en __init__ de repositorios
        return object()

    # Para ConsecutiveTicketRepository, que usa atributo .consecutive_tickets
    consecutive_tickets = object()


@pytest.mark.asyncio
async def test_create_and_get_next_consecutive_and_get_by_code():
    service = TicketService(database=_DummyDB())
    service.repository = FakeTicketRepo()
    service.consecutive_repository = FakeConsecutiveRepo()

    # preview
    prev = await service.get_next_consecutive()
    assert prev.startswith("T-") and prev.endswith("-001")

    created = await service.create_ticket(_payload(), user_id="user-123")
    assert created.ticket_code.endswith("-001")
    got = await service.get_ticket_by_code(created.ticket_code)
    assert got.ticket_code == created.ticket_code


@pytest.mark.asyncio
async def test_list_search_count_and_get_user_tickets():
    service = TicketService(database=_DummyDB())
    service.repository = FakeTicketRepo()
    service.consecutive_repository = FakeConsecutiveRepo()

    # Crear dos tickets
    t1 = await service.create_ticket(_payload(), user_id="user-123")
    t2 = await service.create_ticket(_payload(), user_id="user-999")
    assert t1 and t2

    lst = await service.list_tickets()
    assert len(lst) == 2

    srch = await service.search_tickets(TicketSearch(search_text="imágenes"))
    assert len(srch) == 2

    cnt = await service.count_tickets(TicketSearch(created_by="user-123"))
    assert cnt == 1

    mine = await service.get_user_tickets("user-123")
    assert len(mine) == 1 and mine[0].ticket_code.endswith("-001")


@pytest.mark.asyncio
async def test_update_permissions_status_change_and_delete():
    service = TicketService(database=_DummyDB())
    service.repository = FakeTicketRepo()
    service.consecutive_repository = FakeConsecutiveRepo()

    created = await service.create_ticket(_payload(), user_id="owner")

    # Sin permiso para actualizar si no es creador ni admin
    with pytest.raises(BadRequestError):
        await service.update_ticket(created.ticket_code, TicketUpdate(title="Nuevo título"), user_id="otro", is_admin=False)

    # Como admin, puede actualizar y cambiar estado
    upd = await service.update_ticket(created.ticket_code, TicketUpdate(title="Actualizado"), user_id="admin", is_admin=True)
    assert upd.title == "Actualizado"

    # Cambiar estado (admin only)
    ch = await service.change_ticket_status(created.ticket_code, TicketStatusUpdate(status=TicketStatusEnum.RESOLVED))
    assert ch.status == TicketStatusEnum.RESOLVED

    # Delete ok
    deleted = await service.delete_ticket(created.ticket_code)
    assert deleted is True

    # Not found luego de borrar
    with pytest.raises(NotFoundError):
        await service.get_ticket_by_code(created.ticket_code)