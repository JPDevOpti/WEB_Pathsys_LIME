"""Service layer for unread cases module."""

from __future__ import annotations

from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.unread_case_repository import UnreadCaseRepository
from ..schemas.unread_case import (
    BulkMarkDeliveredRequest,
    BulkMarkDeliveredResponse,
    UnreadCaseCreate,
    UnreadCaseFilter,
    UnreadCaseListResponse,
    UnreadCaseResponse,
    UnreadCaseUpdate,
)
from app.core.exceptions import ConflictError, NotFoundError


class UnreadCaseService:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.repository = UnreadCaseRepository(database)

    async def ensure_indexes(self) -> None:
        await self.repository.ensure_indexes()

    async def list_unread_cases(self, filters: UnreadCaseFilter) -> UnreadCaseListResponse:
        docs, total = await self.repository.list(filters)
        items = [UnreadCaseResponse(**doc) for doc in docs if doc]
        return UnreadCaseListResponse(items=items, total=total, page=filters.page, limit=filters.limit)

    async def get_unread_case(self, case_code: str) -> UnreadCaseResponse:
        found = await self.repository.get_by_case_code(case_code)
        if not found:
            raise NotFoundError(f"Caso sin lectura {case_code} no encontrado")
        return UnreadCaseResponse(**found)

    async def create_unread_case(self, data: UnreadCaseCreate) -> UnreadCaseResponse:
        case_code = data.case_code or await self.repository.generate_case_code()
        if await self.repository.exists_case_code(case_code):
            raise ConflictError(f"El código {case_code} ya existe")

        if data.number_of_plates <= 0 and data.test_groups:
            total = sum(test.quantity for group in data.test_groups for test in group.tests)
            data.number_of_plates = total

        created = await self.repository.create(data, case_code)
        return UnreadCaseResponse(**created)

    async def update_unread_case(self, case_code: str, update: UnreadCaseUpdate) -> UnreadCaseResponse:
        if update.number_of_plates is None and update.test_groups:
            total = sum(test.quantity for group in update.test_groups for test in group.tests)
            update.number_of_plates = total

        updated = await self.repository.update_by_case_code(case_code, update)
        if not updated:
            raise NotFoundError(f"Caso sin lectura {case_code} no encontrado")
        return UnreadCaseResponse(**updated)

    async def mark_delivered(self, payload: BulkMarkDeliveredRequest) -> BulkMarkDeliveredResponse:
        updated = await self.repository.mark_delivered(payload.case_codes, payload.delivered_to, payload.delivery_date)
        items = [UnreadCaseResponse(**doc) for doc in updated if doc]
        return BulkMarkDeliveredResponse(updated=items)


_service: Optional[UnreadCaseService] = None


def get_unread_case_service(database: AsyncIOMotorDatabase) -> UnreadCaseService:
    return UnreadCaseService(database)

