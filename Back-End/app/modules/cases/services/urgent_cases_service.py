from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.cases.repositories.urgent_cases_repository import UrgentCasesRepository


class UrgentCasesService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = UrgentCasesRepository(db)

    async def list_urgent(self, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        return await self.repo.find_urgent_cases(limit=limit, min_days=min_days)

    async def list_urgent_by_pathologist(self, code: str, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        return await self.repo.find_urgent_cases(limit=limit, min_days=min_days, pathologist_code=code)


