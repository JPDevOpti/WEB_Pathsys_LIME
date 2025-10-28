from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.modules.tickets.routes.ticket_routes import router, get_ticket_service
from app.modules.tickets.services.ticket_service import TicketService
from app.modules.tickets.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketStatusUpdate,
    TicketResponse,
    TicketListResponse,
)
from app.modules.tickets.models.ticket import TicketStatusEnum, TicketCategoryEnum
from app.modules.auth.routes.auth_routes import get_current_user_id
from app.core.exceptions import NotFoundError, BadRequestError


class FakeService(TicketService):
    def __init__(self):
        self._store = {}
        self._consec = 0

    async def get_next_consecutive(self) -> str:
        year = datetime.now().year
        return f"T-{year}-{(self._consec + 1):03d}"

    async def create_ticket(self, ticket_data: TicketCreate, user_id: str) -> TicketResponse:
        self._consec += 1
        year = datetime.now().year
        code = f"T-{year}-{self._consec:03d}"
        now = datetime.now(timezone.utc)
        doc = TicketResponse(
            ticket_code=code,
            title=ticket_data.title,
            category=ticket_data.category,
            description=ticket_data.description,
            image=ticket_data.image,
            ticket_date=now,
            status=TicketStatusEnum.OPEN,
            created_by=user_id,
        )
        self._store[code] = doc
        return doc

    async def list_tickets(self, skip=0, limit=20, sort_by="ticket_date", sort_order="desc"):
        items = list(self._store.values())
        return [TicketListResponse(**i.model_dump()) for i in items[skip: skip + limit]]

    async def search_tickets(self, search_params, skip=0, limit=20, sort_by="ticket_date", sort_order="desc"):
        items = list(self._store.values())
        if search_params.search_text:
            txt = search_params.search_text.lower()
            items = [i for i in items if txt in i.title.lower() or txt in i.description.lower()]
        return [TicketListResponse(**i.model_dump()) for i in items[skip: skip + limit]]

    async def count_tickets(self, search_params) -> int:
        items = await self.search_tickets(search_params)
        return len(items)

    async def get_ticket_by_code(self, code: str) -> TicketResponse:
        doc = self._store.get(code)
        if not doc:
            raise NotFoundError("No encontrado")
        return doc

    async def update_ticket(self, code: str, ticket_data: TicketUpdate, user_id: str, is_admin: bool = True):
        doc = self._store.get(code)
        if not doc:
            raise NotFoundError("No encontrado")
        data = ticket_data.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(doc, k, v)
        return doc

    async def change_ticket_status(self, code: str, status_data: TicketStatusUpdate):
        doc = self._store.get(code)
        if not doc:
            raise NotFoundError("No encontrado")
        doc.status = status_data.status
        return doc

    async def delete_ticket(self, code: str) -> bool:
        if code in self._store:
            self._store.pop(code)
            return True
        raise NotFoundError("No encontrado")

    async def upload_ticket_image(self, code: str, file: UploadFile, user_id: str, is_admin: bool = True):
        doc = self._store.get(code)
        if not doc:
            raise NotFoundError("No encontrado")
        content = await file.read()
        if not content:
            raise BadRequestError("Sin contenido")
        doc.image = "data:image/png;base64,AAA"
        return {"image_url": doc.image, "message": "Image uploaded successfully"}

    async def delete_ticket_image(self, code: str, user_id: str, is_admin: bool = True):
        doc = self._store.get(code)
        if not doc:
            raise NotFoundError("No encontrado")
        if not doc.image:
            raise BadRequestError("Sin imagen")
        doc.image = None
        return {"message": "Image deleted successfully"}


def create_app():
    app = FastAPI()
    service = FakeService()
    app.dependency_overrides[get_ticket_service] = lambda: service
    app.dependency_overrides[get_current_user_id] = lambda: "user-123"
    app.include_router(router, prefix="/tickets")
    return app


def _payload():
    return TicketCreate(
        title="Fallo en carga de imágenes",
        category=TicketCategoryEnum.TECHNICAL,
        description="No se pueden cargar imágenes en el formulario",
        image=None,
    )


def test_route_create_list_search_count_and_get():
    app = create_app()
    client = TestClient(app)

    r1 = client.post("/tickets/", json=_payload().model_dump())
    assert r1.status_code == 200
    code = r1.json()["ticket_code"]

    lst = client.get("/tickets/?skip=0&limit=10")
    assert lst.status_code == 200 and isinstance(lst.json(), list) and len(lst.json()) == 1

    srch = client.post("/tickets/search?skip=0&limit=10", json={"search_text": "imágenes"})
    assert srch.status_code == 200 and len(srch.json()) == 1

    cnt = client.get("/tickets/count", params={"search_text": "imágenes"})
    assert cnt.status_code == 200 and cnt.json()["total"] == 1

    one = client.get(f"/tickets/{code}")
    assert one.status_code == 200 and one.json()["ticket_code"] == code


def test_route_update_change_status_delete_and_consecutive_and_images():
    app = create_app()
    client = TestClient(app)

    created = client.post("/tickets/", json=_payload().model_dump())
    assert created.status_code == 200
    code = created.json()["ticket_code"]

    upd = client.put(f"/tickets/{code}", json=TicketUpdate(title="Actualizado").model_dump(exclude_unset=True))
    assert upd.status_code == 200 and upd.json()["title"] == "Actualizado"

    status_change = client.patch(
        f"/tickets/{code}/status",
        json=TicketStatusUpdate(status=TicketStatusEnum.RESOLVED).model_dump(),
    )
    assert status_change.status_code == 200 and status_change.json()["status"] == TicketStatusEnum.RESOLVED

    # preview consecutivo
    nxt = client.get("/tickets/next-consecutive")
    assert nxt.status_code == 200 and "consecutive_code" in nxt.json()

    # upload image
    files = {"image": ("foto.png", b"PNGDATA", "image/png")}
    up = client.post(f"/tickets/{code}/upload-image", files=files)
    assert up.status_code == 200 and up.json()["image_url"].startswith("data:")

    # delete image
    di = client.delete(f"/tickets/{code}/image")
    assert di.status_code == 200

    # delete ticket
    d = client.delete(f"/tickets/{code}")
    assert d.status_code == 200

    # get no encontrado
    nf = client.get(f"/tickets/{code}")
    assert nf.status_code == 404