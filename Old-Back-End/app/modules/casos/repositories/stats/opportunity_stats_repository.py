"""Repositorio de estadísticas de oportunidad por mes."""

from datetime import datetime
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase


class OpportunityStatsRepository:
    def __init__(self, database: AsyncIOMotorDatabase, oportunidad_dias_max: int = 5):
        self.db = database
        self.collection = database.casos
        self.oportunidad_dias_max = oportunidad_dias_max

    def _month_ranges(self, now: Optional[datetime] = None) -> Dict[str, datetime]:
        now = now or datetime.utcnow()
        start_curr = datetime(now.year, now.month, 1)
        if now.month == 1:
            start_prev = datetime(now.year - 1, 12, 1)
            start_prev_prev = datetime(now.year - 1, 11, 1)
        elif now.month == 2:
            start_prev = datetime(now.year, 1, 1)
            start_prev_prev = datetime(now.year - 1, 12, 1)
        else:
            start_prev = datetime(now.year, now.month - 1, 1)
            start_prev_prev = datetime(now.year, now.month - 2, 1)
        end_prev = start_curr
        end_prev_prev = start_prev
        return {
            "start_prev": start_prev,
            "end_prev": end_prev,
            "start_prev_prev": start_prev_prev,
            "end_prev_prev": end_prev_prev,
        }

    async def _oportunidad_mes(self, start: datetime, end: datetime, patologo_codigo: Optional[str] = None) -> Dict[str, Any]:
        base_match: Dict[str, Any] = {"estado": "Completado"}
        if patologo_codigo:
            base_match["patologo_asignado.codigo"] = patologo_codigo

        # Denominador: casos COMPLETADOS con fecha_entrega en el mes. Métrica: días entre fecha_creacion y fecha_firma
        pipeline = [
            {"$match": base_match} if base_match else {"$match": {"_id": {"$exists": True}}},
            {"$match": {"fecha_entrega": {"$gte": start, "$lt": end}}},
            {"$addFields": {"dias": {"$cond": [
                {"$ne": ["$fecha_firma", None]},
                {"$ceil": {"$divide": [
                    {"$dateDiff": {"startDate": "$fecha_creacion", "endDate": "$fecha_firma", "unit": "hour"}},
                    24
                ]}},
                None
            ]}}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "dentro": {"$sum": {"$cond": [
                    {"$and": [
                        {"$ne": ["$dias", None]},
                        {"$lte": ["$dias", self.oportunidad_dias_max]}
                    ]}, 1, 0
                ]}},
                "fuera": {"$sum": {"$cond": [
                    {"$or": [
                        {"$eq": ["$dias", None]},
                        {"$gt": ["$dias", self.oportunidad_dias_max]}
                    ]}, 1, 0
                ]}},
                "gt5": {"$sum": {"$cond": [{"$gt": ["$dias", 5]}, 1, 0]}},
                "gt10": {"$sum": {"$cond": [{"$gt": ["$dias", 10]}, 1, 0]}},
                "gt15": {"$sum": {"$cond": [{"$gt": ["$dias", 15]}, 1, 0]}},
                "max_dias": {"$max": "$dias"},
                "tiempo_promedio": {"$avg": "$dias"}
            }}
        ]
        res = await self.collection.aggregate(pipeline, allowDiskUse=True).to_list(length=1)
        if not res:
            return {"total": 0, "dentro": 0, "fuera": 0, "tiempo_promedio": 0.0}
        doc = res[0]
        total = int(doc.get("total", 0))
        dentro = int(doc.get("dentro", 0))
        fuera = max(0, total - dentro)
        tiempo_promedio = float(doc.get("tiempo_promedio", 0.0) or 0.0)
        return {"total": total, "dentro": dentro, "fuera": fuera, "tiempo_promedio": tiempo_promedio}

    async def get_oportunidad_mes_anterior(self) -> Dict[str, Any]:
        rng = self._month_ranges()
        mes_ant = await self._oportunidad_mes(rng["start_prev"], rng["end_prev"])
        mes_ant_ant = await self._oportunidad_mes(rng["start_prev_prev"], rng["end_prev_prev"])
        return {"mes_anterior": mes_ant, "mes_anterior_anterior": mes_ant_ant, "rangos": rng}

    async def get_oportunidad_mes_anterior_patologo(self, patologo_codigo: str) -> Dict[str, Any]:
        if not patologo_codigo:
            return await self.get_oportunidad_mes_anterior()
        rng = self._month_ranges()
        mes_ant = await self._oportunidad_mes(rng["start_prev"], rng["end_prev"], patologo_codigo)
        mes_ant_ant = await self._oportunidad_mes(rng["start_prev_prev"], rng["end_prev_prev"], patologo_codigo)
        return {"mes_anterior": mes_ant, "mes_anterior_anterior": mes_ant_ant, "rangos": rng}

 
