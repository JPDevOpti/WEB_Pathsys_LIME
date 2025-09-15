"""Repositorio de estadísticas por entidades (placeholder)."""

from typing import Any

class EntitiesStatsRepository:
    def __init__(self, database: Any):
        self.database = database
        self.collection = database.casos


