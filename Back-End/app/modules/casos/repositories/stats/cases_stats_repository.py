"""Repositorio de estadísticas generales de casos (placeholder)."""

from typing import Any

class CasesStatsRepository:
    def __init__(self, database: Any):
        self.database = database
        self.collection = database.casos


