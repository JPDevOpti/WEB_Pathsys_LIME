"""Repositorio de estadísticas mensuales: agrega en MongoDB sin traer todos los documentos."""

from typing import Any, Dict, List
from datetime import datetime, timedelta


class MonthlyStatsRepository:
    def __init__(self, database: Any):
        self.database = database
        self.collection = database.casos

    async def get_casos_por_mes(self, year: int) -> Dict[str, Any]:
        """Conteo de casos por mes del año dado."""
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        pipeline = [
            {"$match": {"fecha_creacion": {"$gte": start, "$lt": end}}},
            {"$group": {"_id": {"$month": "$fecha_creacion"}, "count": {"$sum": 1}}},
        ]
        res: List[Dict[str, Any]] = await self.collection.aggregate(pipeline, allowDiskUse=True).to_list(length=None)
        datos = [0] * 12
        for item in res:
            idx = (int(item.get("_id", 0)) - 1) if item.get("_id") else -1
            if 0 <= idx < 12:
                datos[idx] = int(item.get("count", 0))
        return {"datos": datos, "total": sum(datos), "año": year}

    async def get_casos_por_mes_patologo(self, year: int, patologo_codigo: str) -> Dict[str, Any]:
        """Conteo de casos por mes filtrado por patólogo asignado."""
        if not patologo_codigo:
            return await self.get_casos_por_mes(year)
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        pipeline = [
            {"$match": {
                "fecha_creacion": {"$gte": start, "$lt": end},
                "patologo_asignado.codigo": patologo_codigo
            }},
            {"$group": {"_id": {"$month": "$fecha_creacion"}, "count": {"$sum": 1}}},
        ]
        res: List[Dict[str, Any]] = await self.collection.aggregate(pipeline, allowDiskUse=True).to_list(length=None)
        datos = [0] * 12
        for item in res:
            idx = (int(item.get("_id", 0)) - 1) if item.get("_id") else -1
            if 0 <= idx < 12:
                datos[idx] = int(item.get("count", 0))
        return {"datos": datos, "total": sum(datos), "año": year}

    async def get_mes_actual(self) -> Dict[str, Dict[str, int]]:
        """Estadísticas mensuales: mes actual, mes anterior y mes anterior al anterior."""
        now = datetime.utcnow()
        start_curr = datetime(now.year, now.month, 1)
        
        # Mes anterior
        if now.month == 1:
            start_prev = datetime(now.year - 1, 12, 1)
        else:
            start_prev = datetime(now.year, now.month - 1, 1)
        end_prev = start_curr
        
        # Mes anterior al anterior
        if now.month == 1:
            start_prev_prev = datetime(now.year - 1, 11, 1)
        elif now.month == 2:
            start_prev_prev = datetime(now.year - 1, 12, 1)
        else:
            start_prev_prev = datetime(now.year, now.month - 2, 1)
        end_prev_prev = start_prev
        # Casos mes actual y anterior
        casos_actual = await self.collection.count_documents({"fecha_creacion": {"$gte": start_curr}})
        casos_anterior = await self.collection.count_documents({"fecha_creacion": {"$gte": start_prev, "$lt": end_prev}})
        casos_anterior_anterior = await self.collection.count_documents({"fecha_creacion": {"$gte": start_prev_prev, "$lt": end_prev_prev}})
        # Pacientes únicos por mes (paciente.paciente_code)
        pacientes_actual_res = await self.collection.aggregate([
            {"$match": {"fecha_creacion": {"$gte": start_curr}}},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_anterior_res = await self.collection.aggregate([
            {"$match": {"fecha_creacion": {"$gte": start_prev, "$lt": end_prev}}},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_anterior_anterior_res = await self.collection.aggregate([
            {"$match": {"fecha_creacion": {"$gte": start_prev_prev, "$lt": end_prev_prev}}},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_actual = int((pacientes_actual_res[0]["total"]) if pacientes_actual_res else 0)
        pacientes_anterior = int((pacientes_anterior_res[0]["total"]) if pacientes_anterior_res else 0)
        pacientes_anterior_anterior = int((pacientes_anterior_anterior_res[0]["total"]) if pacientes_anterior_anterior_res else 0)
        return {
            "pacientes": {"mes_actual": pacientes_actual, "mes_anterior": pacientes_anterior, "mes_anterior_anterior": pacientes_anterior_anterior},
            "casos": {"mes_actual": casos_actual, "mes_anterior": casos_anterior, "mes_anterior_anterior": casos_anterior_anterior}
        }

    async def get_mes_actual_patologo(self, patologo_codigo: str) -> Dict[str, Dict[str, int]]:
        """Estadísticas mensuales filtradas por patólogo: actual, anterior y anterior-anterior."""
        if not patologo_codigo:
            return await self.get_mes_actual()
        now = datetime.utcnow()
        start_curr = datetime(now.year, now.month, 1)
        
        # Mes anterior
        if now.month == 1:
            start_prev = datetime(now.year - 1, 12, 1)
        else:
            start_prev = datetime(now.year, now.month - 1, 1)
        end_prev = start_curr
        
        # Mes anterior al anterior
        if now.month == 1:
            start_prev_prev = datetime(now.year - 1, 11, 1)
        elif now.month == 2:
            start_prev_prev = datetime(now.year - 1, 12, 1)
        else:
            start_prev_prev = datetime(now.year, now.month - 2, 1)
        end_prev_prev = start_prev
        match_curr = {"fecha_creacion": {"$gte": start_curr}, "patologo_asignado.codigo": patologo_codigo}
        match_prev = {"fecha_creacion": {"$gte": start_prev, "$lt": end_prev}, "patologo_asignado.codigo": patologo_codigo}
        match_prev_prev = {"fecha_creacion": {"$gte": start_prev_prev, "$lt": end_prev_prev}, "patologo_asignado.codigo": patologo_codigo}
        casos_actual = await self.collection.count_documents(match_curr)
        casos_anterior = await self.collection.count_documents(match_prev)
        casos_anterior_anterior = await self.collection.count_documents(match_prev_prev)
        pacientes_actual_res = await self.collection.aggregate([
            {"$match": match_curr},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_anterior_res = await self.collection.aggregate([
            {"$match": match_prev},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_anterior_anterior_res = await self.collection.aggregate([
            {"$match": match_prev_prev},
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]).to_list(length=1)
        pacientes_actual = int((pacientes_actual_res[0]["total"]) if pacientes_actual_res else 0)
        pacientes_anterior = int((pacientes_anterior_res[0]["total"]) if pacientes_anterior_res else 0)
        pacientes_anterior_anterior = int((pacientes_anterior_anterior_res[0]["total"]) if pacientes_anterior_anterior_res else 0)
        return {
            "pacientes": {"mes_actual": pacientes_actual, "mes_anterior": pacientes_anterior, "mes_anterior_anterior": pacientes_anterior_anterior},
            "casos": {"mes_actual": casos_actual, "mes_anterior": casos_anterior, "mes_anterior_anterior": casos_anterior_anterior}
        }


