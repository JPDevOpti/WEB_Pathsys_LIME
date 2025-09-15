"""Servicio de estadísticas de oportunidad: orquesta repo y caché."""

from typing import Any, Dict

from app.modules.casos.repositories.stats.opportunity_stats_repository import OpportunityStatsRepository


class OpportunityStatsService:
    def __init__(self, database: Any, oportunidad_dias_max: int = 5):
        self.repo = OpportunityStatsRepository(database, oportunidad_dias_max)
        from app.modules.casos.services.cache_service import cache_service
        self.cache = cache_service

    def _pct(self, a: float, b: float) -> float:
        denom = b if b > 0 else 1
        return round(((a - b) / denom) * 100, 2)

    async def mes_anterior(self) -> Dict[str, Any]:
        key = "oportunidad:mes_anterior:v2"
        cached = await self.cache.get(key)
        if cached is not None:
            return cached
        base = await self.repo.get_oportunidad_mes_anterior()
        a = base["mes_anterior"]
        b = base["mes_anterior_anterior"]
        porc_a = round((a["dentro"] / a["total"] * 100) if a["total"] else 0.0, 2)
        porc_b = round((b["dentro"] / b["total"] * 100) if b["total"] else 0.0, 2)
        out = {
            "porcentaje_oportunidad": porc_a,
            "cambio_porcentual": self._pct(porc_a, porc_b),
            "tiempo_promedio": round(a["tiempo_promedio"], 2) if a else 0.0,
            "casos_dentro_oportunidad": a["dentro"],
            "casos_fuera_oportunidad": a["fuera"],
            "total_casos_mes_anterior": a["total"],
            "debug": {"gt5": a.get("gt5", 0), "gt10": a.get("gt10", 0), "gt15": a.get("gt15", 0), "max_dias": a.get("max_dias", 0)},
            "mes_anterior": {
                "nombre": "Mes anterior",
                "inicio": base["rangos"]["start_prev"].isoformat(),
                "fin": base["rangos"]["end_prev"].isoformat(),
            },
        }
        await self.cache.set(key, out, 300)
        return out

    async def mes_anterior_por_patologo(self, patologo_codigo: str) -> Dict[str, Any]:
        key = f"oportunidad:mes_anterior:v2:pat:{patologo_codigo}"
        cached = await self.cache.get(key)
        if cached is not None:
            return cached
        base = await self.repo.get_oportunidad_mes_anterior_patologo(patologo_codigo)
        a = base["mes_anterior"]
        b = base["mes_anterior_anterior"]
        porc_a = round((a["dentro"] / a["total"] * 100) if a["total"] else 0.0, 2)
        porc_b = round((b["dentro"] / b["total"] * 100) if b["total"] else 0.0, 2)
        out = {
            "porcentaje_oportunidad": porc_a,
            "cambio_porcentual": self._pct(porc_a, porc_b),
            "tiempo_promedio": round(a["tiempo_promedio"], 2) if a else 0.0,
            "casos_dentro_oportunidad": a["dentro"],
            "casos_fuera_oportunidad": a["fuera"],
            "total_casos_mes_anterior": a["total"],
            "debug": {"gt5": a.get("gt5", 0), "gt10": a.get("gt10", 0), "gt15": a.get("gt15", 0), "max_dias": a.get("max_dias", 0)},
            "mes_anterior": {
                "nombre": "Mes anterior",
                "inicio": base["rangos"]["start_prev"].isoformat(),
                "fin": base["rangos"]["end_prev"].isoformat(),
            },
        }
        await self.cache.set(key, out, 300)
        return out


