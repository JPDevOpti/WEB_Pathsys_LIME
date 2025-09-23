"""Repositorio para manejo de códigos consecutivos de aprobaciones."""

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class ApprovalConsecutiveRepository:
    """Repositorio para generar códigos consecutivos de aprobaciones."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.approval_counters

    async def ensure_indexes(self):
        """Crear índices necesarios."""
        await self.collection.create_index("year", unique=True)

    async def get_next_number(self, year: int) -> int:
        """Obtener el siguiente número consecutivo para un año."""
        now = datetime.utcnow()
        doc = await self.collection.find_one_and_update(
            {"year": year},
            {"$inc": {"last_number": 1}, "$set": {"updated_at": now}},
            upsert=True,
            return_document=True
        )
        return int(doc.get("last_number", 1))

    async def peek_next_number(self, year: int) -> int:
        """Obtener el siguiente número sin incrementarlo."""
        doc = await self.collection.find_one({"year": year})
        return int(doc.get("last_number", 0)) + 1 if doc else 1

    async def generate_approval_code(self, year: int | None = None) -> str:
        """Generar código completo de aprobación (AP-YYYY-NNN)."""
        y = year or datetime.utcnow().year
        n = await self.get_next_number(y)
        return f"AP-{y}-{n:03d}"
