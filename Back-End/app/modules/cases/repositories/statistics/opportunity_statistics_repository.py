# Opportunity Statistics Repository
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class OpportunityStatisticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cases

    def _month_range(self, ref: Optional[datetime] = None) -> Dict[str, datetime]:
        now = ref or datetime.utcnow()
        current_month_start = datetime(now.year, now.month, 1)
        if now.month == 1:
            previous_month_start = datetime(now.year - 1, 12, 1)
        else:
            previous_month_start = datetime(now.year, now.month - 1, 1)

        # Start of the month before the previous
        if previous_month_start.month == 1:
            pre_previous_month_start = datetime(previous_month_start.year - 1, 12, 1)
        else:
            pre_previous_month_start = datetime(previous_month_start.year, previous_month_start.month - 1, 1)

        return {
            "current_month_start": current_month_start,
            "previous_month_start": previous_month_start,
            "pre_previous_month_start": pre_previous_month_start,
        }

    async def _compute_opportunity_for_range(
        self,
        start_date: datetime,
        end_date: datetime,
        pathologist_code: Optional[str] = None,
        opportunity_days_threshold: int = 7,
    ) -> Dict[str, Any]:
        match_stage: Dict[str, Any] = {
            "signed_at": {"$gte": start_date, "$lt": end_date},
        }
        if pathologist_code:
            match_stage["assigned_pathologist.id"] = pathologist_code

        # Traer solo los campos necesarios para minimizar payload
        projection = {
            "created_at": 1,
            "signed_at": 1,
            "state": 1,
            "assigned_pathologist.id": 1,
            "_id": 0,
        }

        cursor = self.collection.find(match_stage, projection=projection)
        docs = await cursor.to_list(length=None)

        # Filtrar a sólo los completados dentro de los firmados el mes consultado
        filtered = [d for d in docs if str(d.get("state")) == "Completado" and d.get("created_at") and d.get("signed_at")]

        total_considerados = len(filtered)
        if total_considerados == 0:
            return {
                "porcentaje_oportunidad": 0.0,
                "tiempo_promedio": 0.0,
                "casos_dentro_oportunidad": 0,
                "casos_fuera_oportunidad": 0,
                "total_casos_mes_anterior": 0,
            }

        diffs_days = []
        dentro = 0
        fuera = 0
        for d in filtered:
            created_at: datetime = d["created_at"]
            signed_at: datetime = d["signed_at"]
            # Diferencia en días naturales con decimales
            delta_days = (signed_at - created_at).total_seconds() / 86400.0
            diffs_days.append(delta_days)
            if delta_days <= float(opportunity_days_threshold):
                dentro += 1
            else:
                fuera += 1

        promedio = sum(diffs_days) / len(diffs_days) if diffs_days else 0.0
        porcentaje = (dentro / total_considerados) * 100.0 if total_considerados else 0.0

        return {
            "porcentaje_oportunidad": round(porcentaje, 2),
            "tiempo_promedio": round(promedio, 2),
            "casos_dentro_oportunidad": dentro,
            "casos_fuera_oportunidad": fuera,
            "total_casos_mes_anterior": total_considerados,
        }

    async def get_opportunity_general(self, opportunity_days_threshold: int = 7) -> Dict[str, Any]:
        rng = self._month_range()
        prev_start = rng["previous_month_start"]
        curr_start = rng["current_month_start"]

        # Mes previo al anterior para calcular cambio porcentual
        pre_prev_start = rng["pre_previous_month_start"]

        current_metrics = await self._compute_opportunity_for_range(
            start_date=prev_start,
            end_date=curr_start,
            pathologist_code=None,
            opportunity_days_threshold=opportunity_days_threshold,
        )

        previous_metrics = await self._compute_opportunity_for_range(
            start_date=pre_prev_start,
            end_date=prev_start,
            pathologist_code=None,
            opportunity_days_threshold=opportunity_days_threshold,
        )

        prev_percent = previous_metrics.get("porcentaje_oportunidad", 0.0)
        curr_percent = current_metrics.get("porcentaje_oportunidad", 0.0)
        if prev_percent > 0:
            cambio = ((curr_percent - prev_percent) / prev_percent) * 100.0
        else:
            cambio = 100.0 if curr_percent > 0 else 0.0

        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_nombre = meses[prev_start.month - 1]

        return {
            **current_metrics,
            "cambio_porcentual": round(cambio, 2),
            "mes_anterior": {
                "nombre": mes_nombre,
                "numero": prev_start.month,
                "inicio": prev_start.isoformat(),
                "fin": (curr_start - timedelta(seconds=1)).isoformat(),
            },
        }

    async def get_opportunity_pathologist(self, pathologist_code: str, opportunity_days_threshold: int = 7) -> Dict[str, Any]:
        if not pathologist_code:
            raise ValueError("pathologist_code requerido")

        rng = self._month_range()
        prev_start = rng["previous_month_start"]
        curr_start = rng["current_month_start"]
        pre_prev_start = rng["pre_previous_month_start"]

        current_metrics = await self._compute_opportunity_for_range(
            start_date=prev_start,
            end_date=curr_start,
            pathologist_code=pathologist_code,
            opportunity_days_threshold=opportunity_days_threshold,
        )

        previous_metrics = await self._compute_opportunity_for_range(
            start_date=pre_prev_start,
            end_date=prev_start,
            pathologist_code=pathologist_code,
            opportunity_days_threshold=opportunity_days_threshold,
        )

        prev_percent = previous_metrics.get("porcentaje_oportunidad", 0.0)
        curr_percent = current_metrics.get("porcentaje_oportunidad", 0.0)
        if prev_percent > 0:
            cambio = ((curr_percent - prev_percent) / prev_percent) * 100.0
        else:
            cambio = 100.0 if curr_percent > 0 else 0.0

        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_nombre = meses[prev_start.month - 1]

        return {
            **current_metrics,
            "cambio_porcentual": round(cambio, 2),
            "mes_anterior": {
                "nombre": mes_nombre,
                "numero": prev_start.month,
                "inicio": prev_start.isoformat(),
                "fin": (curr_start - timedelta(seconds=1)).isoformat(),
            },
        }
