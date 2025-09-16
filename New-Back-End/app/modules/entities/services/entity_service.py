from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import EntityCreate, EntityUpdate, EntityResponse, EntitySearch
from ..repositories import EntityRepository
from app.core.exceptions import BadRequestError, NotFoundError, ConflictError

class EntityService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = EntityRepository(database)

    async def create_entity(self, data: EntityCreate) -> EntityResponse:
        if await self.repository.exists_code(data.entity_code):
            raise ConflictError(f"Entity with code {data.entity_code} already exists")
        created = await self.repository.create(data)
        return EntityResponse(**created)

    async def get_by_code(self, code: str) -> EntityResponse:
        found = await self.repository.get_by_code(code)
        if not found:
            raise NotFoundError(f"Entity with code {code} not found")
        return EntityResponse(**found)

    async def list_active(self, search: EntitySearch) -> List[EntityResponse]:
        docs = await self.repository.list_active(search)
        return [EntityResponse(**d) for d in docs]

    async def list_all(self, search: EntitySearch) -> List[EntityResponse]:
        docs = await self.repository.list_all(search)
        return [EntityResponse(**d) for d in docs]

    async def update_by_code(self, code: str, update: EntityUpdate) -> EntityResponse:
        if update.entity_code and update.entity_code.upper() != code.upper():
            if await self.repository.exists_code(update.entity_code):
                raise ConflictError(f"Entity with code {update.entity_code} already exists")
        updated = await self.repository.update_by_code(code, update)
        if not updated:
            raise NotFoundError(f"Entity with code {code} not found")
        return EntityResponse(**updated)

    async def delete_by_code(self, code: str) -> bool:
        if not await self.repository.get_by_code(code):
            raise NotFoundError(f"Entity with code {code} not found")
        return await self.repository.delete_by_code(code)

entity_service: Optional[EntityService] = None

def get_entity_service(database: AsyncIOMotorDatabase) -> EntityService:
    return EntityService(database)
