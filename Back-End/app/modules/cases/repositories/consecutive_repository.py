"""
Repositorio de consecutivos de casos: gestiona numeración anual y código.
"""
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase


class CaseConsecutiveRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.case_counters

    # Índice único por año para controlar el contador.
    async def ensure_indexes(self):
        await self.collection.create_index("year", unique=True)

    # Incrementa y retorna el siguiente número del año dado.
    async def get_next_number(self, year: int) -> int:
        now = datetime.now(timezone.utc)
        doc = await self.collection.find_one_and_update(
            {"year": year},
            {"$inc": {"last_number": 1}, "$set": {"updated_at": now}},
            upsert=True,
            return_document=True
        )
        return int(doc.get("last_number", 1))

    # Consulta el próximo número sin incrementar.
    async def peek_next_number(self, year: int) -> int:
        doc = await self.collection.find_one({"year": year})
        return int(doc.get("last_number", 0)) + 1 if doc else 1

    # Genera el código del caso basado en año y consecutivo.
    async def generate_case_code(self, year: int = None) -> str:
        y = year or datetime.now(timezone.utc).year
        n = await self.get_next_number(y)
        return f"{y}-{n:05d}"


