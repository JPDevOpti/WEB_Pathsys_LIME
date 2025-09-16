"""Servicio de estadísticas mensuales: orquesta repositorio y caché."""

from typing import Any, Dict
from app.modules.casos.schemas.stats import DashboardMetricsResponse, MesActualStats


class MonthlyStatsService:
    def __init__(self, database: Any):
        self.database = database
        from app.modules.casos.services.cache_service import cache_service
        from app.modules.casos.repositories.stats.monthly_stats_repository import MonthlyStatsRepository
        self.cache = cache_service
        self.repo = MonthlyStatsRepository(database)

    async def casos_por_mes(self, year: int, no_cache: bool = False) -> Dict[str, Any]:
        key = f"casos_por_mes:{year}"
        if not no_cache:
            cached = await self.cache.get(key)
            if cached is not None:
                return cached
        data = await self.repo.get_casos_por_mes(year)
        if not no_cache:
            await self.cache.set(key, data, 600)
        return data

    async def casos_por_mes_patologo(self, year: int, patologo_codigo: str, no_cache: bool = False) -> Dict[str, Any]:
        key = f"casos_por_mes_patologo:{year}:{patologo_codigo}"
        if not no_cache:
            cached = await self.cache.get(key)
            if cached is not None:
                return cached
        data = await self.repo.get_casos_por_mes_patologo(year, patologo_codigo)
        if not no_cache:
            await self.cache.set(key, data, 600)
        return data

    async def mes_actual(self, no_cache: bool = False) -> Dict[str, Dict[str, int | float]]:
        """Resumen mensual (mes actual vs anterior) para pacientes y casos."""
        key = "mes_actual:general"
        if not no_cache:
            cached = await self.cache.get(key)
            if cached is not None:
                return cached
        base = await self.repo.get_mes_actual()
        out = {
            "pacientes": {
                "mes_actual": base["pacientes"]["mes_actual"],
                "mes_anterior": base["pacientes"]["mes_anterior"],
                "mes_anterior_anterior": base["pacientes"].get("mes_anterior_anterior"),
                "cambio_porcentual": self._pct(base["pacientes"]["mes_anterior"], base["pacientes"].get("mes_anterior_anterior", 0)),
            },
            "casos": {
                "mes_actual": base["casos"]["mes_actual"],
                "mes_anterior": base["casos"]["mes_anterior"],
                "mes_anterior_anterior": base["casos"].get("mes_anterior_anterior"),
                "cambio_porcentual": self._pct(base["casos"]["mes_anterior"], base["casos"].get("mes_anterior_anterior", 0)),
            }
        }
        if not no_cache:
            await self.cache.set(key, out, 300)
        return out

    async def mes_actual_por_patologo(self, patologo_codigo: str, no_cache: bool = False) -> Dict[str, Dict[str, int | float]]:
        key = f"mes_actual:patologo:{patologo_codigo}"
        if not no_cache:
            cached = await self.cache.get(key)
            if cached is not None:
                return cached
        base = await self.repo.get_mes_actual_patologo(patologo_codigo)
        out = {
            "pacientes": {
                "mes_actual": base["pacientes"]["mes_actual"],
                "mes_anterior": base["pacientes"]["mes_anterior"],
                "mes_anterior_anterior": base["pacientes"].get("mes_anterior_anterior"),
                "cambio_porcentual": self._pct(base["pacientes"]["mes_anterior"], base["pacientes"].get("mes_anterior_anterior", 0)),
            },
            "casos": {
                "mes_actual": base["casos"]["mes_actual"],
                "mes_anterior": base["casos"]["mes_anterior"],
                "mes_anterior_anterior": base["casos"].get("mes_anterior_anterior"),
                "cambio_porcentual": self._pct(base["casos"]["mes_anterior"], base["casos"].get("mes_anterior_anterior", 0)),
            }
        }
        if not no_cache:
            await self.cache.set(key, out, 300)
        return out

    def _pct(self, actual: int, anterior: int) -> float:
        denom = anterior if anterior > 0 else 1
        return round(((actual - anterior) / denom) * 100, 2)


