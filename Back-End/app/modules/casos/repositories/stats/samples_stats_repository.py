"""Repositorio de estadísticas de muestras (placeholder)."""

from typing import Any

class SamplesStatsRepository:
    def __init__(self, database: Any):
        self.database = database
        self.collection = database.casos


