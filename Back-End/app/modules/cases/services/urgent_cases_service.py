from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.cases.repositories.urgent_cases_repository import UrgentCasesRepository


class UrgentCasesService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = UrgentCasesRepository(db)

    async def list_urgent(self, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        # Transform repository output (English keys) into Spanish keys for UI/Frontend
        items = await self.repo.find_urgent_cases(limit=limit, min_days=min_days)
        return [
            {
                "caso_code": i.get("case_code"),
                "paciente_nombre": i.get("patient_name"),
                "paciente_documento": i.get("patient_code"),
                "entidad_nombre": i.get("entity_name"),
                "pruebas": i.get("tests") or [],
                "patologo_nombre": i.get("pathologist_name"),
                "fecha_creacion": i.get("created_at"),
                "estado": i.get("state"),
                "prioridad": i.get("priority"),
                "dias_habiles_transcurridos": i.get("days_in_system") or 0,
            }
            for i in items
        ]

    async def list_urgent_by_pathologist(self, code: str, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        # Transform repository output (English keys) into Spanish keys for UI/Frontend
        items = await self.repo.find_urgent_cases(limit=limit, min_days=min_days, pathologist_code=code)
        return [
            {
                "caso_code": i.get("case_code"),
                "paciente_nombre": i.get("patient_name"),
                "paciente_documento": i.get("patient_code"),
                "entidad_nombre": i.get("entity_name"),
                "pruebas": i.get("tests") or [],
                "patologo_nombre": i.get("pathologist_name"),
                "fecha_creacion": i.get("created_at"),
                "estado": i.get("state"),
                "prioridad": i.get("priority"),
                "dias_habiles_transcurridos": i.get("days_in_system") or 0,
            }
            for i in items
        ]


