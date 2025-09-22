from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import TestCreate, TestUpdate, TestResponse, TestSearch
from ..repositories import TestRepository
from app.core.exceptions import NotFoundError, ConflictError

class TestService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = TestRepository(database)

    async def create_test(self, data: TestCreate) -> TestResponse:
        if await self.repository.exists_code(data.test_code):
            raise ConflictError(f"Test with code {data.test_code} already exists")
        created = await self.repository.create(data)
        return TestResponse(**created)

    async def get_by_code(self, code: str) -> TestResponse:
        found = await self.repository.get_by_code(code)
        if not found:
            raise NotFoundError(f"Test with code {code} not found")
        return TestResponse(**found)

    async def list_active(self, search: TestSearch) -> List[TestResponse]:
        docs = await self.repository.list_active(search)
        return [TestResponse(**d) for d in docs]

    async def list_all(self, search: TestSearch) -> List[TestResponse]:
        docs = await self.repository.list_all(search)
        return [TestResponse(**d) for d in docs]

    async def update_by_code(self, code: str, update: TestUpdate) -> TestResponse:
        if update.test_code and update.test_code.upper() != code.upper():
            if await self.repository.exists_code(update.test_code):
                raise ConflictError(f"Test with code {update.test_code} already exists")
        updated = await self.repository.update_by_code(code, update)
        if not updated:
            raise NotFoundError(f"Test with code {code} not found")
        return TestResponse(**updated)

    async def delete_by_code(self, code: str) -> bool:
        if not await self.repository.get_by_code(code):
            raise NotFoundError(f"Test with code {code} not found")
        return await self.repository.delete_by_code(code)

_test_service: Optional[TestService] = None

def get_test_service(database: AsyncIOMotorDatabase) -> TestService:
    return TestService(database)
