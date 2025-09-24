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
            "signed_at": 1,
            "state": 1,
            "assigned_pathologist.id": 1,
            "business_days": 1,
            "_id": 0,
        }

        cursor = self.collection.find(match_stage, projection=projection)
        docs = await cursor.to_list(length=None)

        # Filtrar a sólo los completados dentro de los firmados el mes consultado
        filtered = [d for d in docs if str(d.get("state")) == "Completado" and d.get("signed_at") and d.get("business_days") is not None]

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
            business_days: int = d["business_days"]
            diffs_days.append(business_days)
            if business_days <= opportunity_days_threshold:
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

    # ---------------------------
    # New English-facing helpers
    # ---------------------------
    def _month_bounds(self, year: int, month: int) -> tuple[datetime, datetime]:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        return start, end

    async def get_monthly_opportunity(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        entity: str | None = None,
        pathologist: str | None = None,
    ) -> dict:
        """Monthly opportunity breakdown for tests and pathologists (English shape).

        - Universe: cases with state == "Completado" and signed_at within month.
        - Time in days = (signed_at - created_at) / 86400.0
        - within if days <= threshold_days
        """
        start, end = self._month_bounds(year, month)

        match_stage: Dict[str, Any] = {
            "state": "Completado",
            "signed_at": {"$gte": start, "$lt": end},
        }

        # Optional filters
        if entity:
            match_stage["patient_info.entity_info.name"] = {"$regex": entity, "$options": "i"}

        if pathologist:
            # Match either by id exact or name regex (case-insensitive)
            match_stage["$or"] = [
                {"assigned_pathologist.id": pathologist},
                {"assigned_pathologist.name": {"$regex": pathologist, "$options": "i"}},
            ]

        projection = {
            "signed_at": 1,
            "state": 1,
            "assigned_pathologist.id": 1,
            "assigned_pathologist.name": 1,
            "patient_info.entity_info.name": 1,
            "samples.tests.id": 1,
            "samples.tests.name": 1,
            "business_days": 1,
            "_id": 0,
        }

        cursor = self.collection.find(match_stage, projection=projection)
        docs = await cursor.to_list(length=None)

        tests_map: Dict[str, Dict[str, Any]] = {}
        pat_map: Dict[str, Dict[str, Any]] = {}
        total = 0
        total_within = 0
        sum_days_all = 0.0

        for d in docs:
            signed_at: Optional[datetime] = d.get("signed_at")
            business_days: Optional[int] = d.get("business_days")
            if not signed_at or business_days is None:
                continue
            days = business_days
            within = days <= threshold_days
            total += 1
            sum_days_all += days
            if within:
                total_within += 1

            # Aggregate by tests
            samples = d.get("samples") or []
            for s in samples:
                for t in s.get("tests", []) or []:
                    code = str(t.get("id") or "")
                    name = str(t.get("name") or "")
                    if not code and not name:
                        continue
                    key = code or name
                    rec = tests_map.get(key)
                    if not rec:
                        rec = {
                            "code": code,
                            "name": name,
                            "within": 0,
                            "out": 0,
                            "sumDays": 0.0,
                            "count": 0,
                        }
                        tests_map[key] = rec
                    rec["sumDays"] += days
                    rec["count"] += 1
                    if within:
                        rec["within"] += 1
                    else:
                        rec["out"] += 1

            # Aggregate by pathologist
            ap = d.get("assigned_pathologist") or {}
            pcode = str(ap.get("id") or "")
            pname = str(ap.get("name") or "")
            pkey = pcode or pname
            if pkey:
                prec = pat_map.get(pkey)
                if not prec:
                    prec = {
                        "code": pcode,
                        "name": pname,
                        "within": 0,
                        "out": 0,
                        "sumDays": 0.0,
                        "count": 0,
                    }
                    pat_map[pkey] = prec
                prec["sumDays"] += days
                prec["count"] += 1
                if within:
                    prec["within"] += 1
                else:
                    prec["out"] += 1

        def to_test_item(v: Dict[str, Any]) -> Dict[str, Any]:
            count = max(1, int(v.get("count", 0)))
            avg = (float(v.get("sumDays", 0.0)) / count) if count else 0.0
            return {
                "code": v.get("code", ""),
                "name": v.get("name", ""),
                "withinOpportunity": int(v.get("within", 0)),
                "outOfOpportunity": int(v.get("out", 0)),
                "averageDays": round(avg, 2),
            }

        def to_pat_item(v: Dict[str, Any]) -> Dict[str, Any]:
            count = max(1, int(v.get("count", 0)))
            avg = (float(v.get("sumDays", 0.0)) / count) if count else 0.0
            return {
                "code": v.get("code", ""),
                "name": v.get("name", ""),
                "withinOpportunity": int(v.get("within", 0)),
                "outOfOpportunity": int(v.get("out", 0)),
                "averageDays": round(avg, 2),
            }

        tests = [to_test_item(v) for v in tests_map.values()]
        pathologists = [to_pat_item(v) for v in pat_map.values()]
        avg_all = round((sum_days_all / total), 2) if total else 0.0

        return {
            "tests": tests,
            "pathologists": pathologists,
            "summary": {
                "total": total,
                "within": total_within,
                "out": total - total_within,
                "averageDays": avg_all,
            },
        }

    async def get_yearly_opportunity(self, year: int, threshold_days: int = 7) -> list[float]:
        """Return 12-month opportunity percentages for a year (English shape)."""
        out: list[float] = []
        for m in range(1, 13):
            monthly = await self.get_monthly_opportunity(m, year, threshold_days)
            total = monthly.get("summary", {}).get("total", 0)
            within = monthly.get("summary", {}).get("within", 0)
            pct = round((within / total) * 100.0, 1) if total else 0.0
            out.append(pct)
        return out
