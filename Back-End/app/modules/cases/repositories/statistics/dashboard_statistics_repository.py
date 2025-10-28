from datetime import datetime, timezone
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase


class DashboardStatisticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cases

    # Cantidad de casos por mes del año indicado.
    async def get_cases_by_month(self, year: int) -> Dict[str, Any]:
        start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lt": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {"$month": "$created_at"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=12)
        monthly_data = [0] * 12
        for result in results:
            month_index = result["_id"] - 1
            if 0 <= month_index < 12:
                monthly_data[month_index] = result["count"]
        
        total = sum(monthly_data)
        
        return {"datos": monthly_data, "total": total, "año": year}

    # Casos por mes filtrados por patólogo (id).
    async def get_cases_by_month_pathologist(self, year: int, pathologist_code: str) -> Dict[str, Any]:
        start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lt": end_date
                    },
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {
                "$group": {
                    "_id": {"$month": "$created_at"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=12)
        monthly_data = [0] * 12
        for result in results:
            month_index = result["_id"] - 1
            if 0 <= month_index < 12:
                monthly_data[month_index] = result["count"]
        
        total = sum(monthly_data)
        
        return {"datos": monthly_data, "total": total, "año": year, "pathologist_code": pathologist_code}

    # Resumen del dashboard actual y mes anterior.
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        current_month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        previous_month_start = (
            datetime(now.year - 1, 12, 1, tzinfo=timezone.utc)
            if now.month == 1
            else datetime(now.year, now.month - 1, 1, tzinfo=timezone.utc)
        )
        next_month_start = (
            datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
            if now.month == 12
            else datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        )
        
        current_month_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": current_month_start,
                        "$lt": next_month_start
                    }
                }
            },
            {
                "$count": "total"
            }
        ]
        previous_month_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": previous_month_start,
                        "$lt": current_month_start
                    }
                }
            },
            {
                "$count": "total"
            }
        ]
        total_pipeline = [
            {
                "$count": "total"
            }
        ]
        cases_by_state_pipeline = [
            {
                "$group": {
                    "_id": "$state",
                    "count": {"$sum": 1}
                }
            }
        ]
        current_month_result = await self.collection.aggregate(current_month_pipeline).to_list(1)
        previous_month_result = await self.collection.aggregate(previous_month_pipeline).to_list(1)
        total_result = await self.collection.aggregate(total_pipeline).to_list(1)
        cases_by_state_result = await self.collection.aggregate(cases_by_state_pipeline).to_list(length=None)
        casos_mes_actual = current_month_result[0]["total"] if current_month_result else 0
        casos_mes_anterior = previous_month_result[0]["total"] if previous_month_result else 0
        total_casos = total_result[0]["total"] if total_result else 0
        if casos_mes_anterior > 0:
            cambio_porcentual = ((casos_mes_actual - casos_mes_anterior) / casos_mes_anterior) * 100
        else:
            cambio_porcentual = 100.0 if casos_mes_actual > 0 else 0.0
        casos_por_estado = {}
        for result in cases_by_state_result:
            casos_por_estado[result["_id"]] = result["count"]
        return {
            "total_casos": total_casos,
            "casos_mes_actual": casos_mes_actual,
            "casos_mes_anterior": casos_mes_anterior,
            "cambio_porcentual": round(cambio_porcentual, 2),
            "casos_por_estado": casos_por_estado,
        }

    async def get_metrics_general(self) -> Dict[str, Any]:
        """Obtener métricas generales del laboratorio"""
        now = datetime.now(timezone.utc)
        current_month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        # Mes anterior
        if now.month == 1:
            previous_month_start = datetime(now.year - 1, 12, 1, tzinfo=timezone.utc)
        else:
            previous_month_start = datetime(now.year, now.month - 1, 1, tzinfo=timezone.utc)
        
        # Próximo mes para el rango
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
        
        # Pipeline para pacientes del mes actual
        current_month_patients_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": current_month_start,
                        "$lt": next_month_start
                    }
                }
            },
            {
                "$addFields": {
                    "patient_key": {
                        "$ifNull": [
                            "$patient_info.patient_code",
                            {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]},
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}
                                        ]
                                    },
                                    {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]},
                                    "$patient_info.identification_number"
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$patient_key",
                    "count": {"$sum": 1}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para pacientes del mes anterior
        previous_month_patients_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": previous_month_start,
                        "$lt": current_month_start
                    }
                }
            },
            {
                "$addFields": {
                    "patient_key": {
                        "$ifNull": [
                            "$patient_info.patient_code",
                            {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]},
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}
                                        ]
                                    },
                                    {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]},
                                    "$patient_info.identification_number"
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$patient_key",
                    "count": {"$sum": 1}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para casos del mes actual
        current_month_cases_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": current_month_start,
                        "$lt": next_month_start
                    }
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para casos del mes anterior
        previous_month_cases_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": previous_month_start,
                        "$lt": current_month_start
                    }
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Ejecutar agregaciones
        current_month_patients_result = await self.collection.aggregate(current_month_patients_pipeline).to_list(1)
        previous_month_patients_result = await self.collection.aggregate(previous_month_patients_pipeline).to_list(1)
        current_month_cases_result = await self.collection.aggregate(current_month_cases_pipeline).to_list(1)
        previous_month_cases_result = await self.collection.aggregate(previous_month_cases_pipeline).to_list(1)
        
        # Procesar resultados
        pacientes_mes_actual = current_month_patients_result[0]["total"] if current_month_patients_result else 0
        pacientes_mes_anterior = previous_month_patients_result[0]["total"] if previous_month_patients_result else 0
        casos_mes_actual = current_month_cases_result[0]["total"] if current_month_cases_result else 0
        casos_mes_anterior = previous_month_cases_result[0]["total"] if previous_month_cases_result else 0
        
        # Calcular cambios porcentuales con ventanas rodantes de 30 días
        from datetime import timedelta
        last30_start = now - timedelta(days=30)
        prev30_start = now - timedelta(days=60)
        prev30_end = last30_start

        # Pacientes últimos 30 días (únicos por clave de paciente)
        last30_patients_pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": last30_start, "$lt": now}
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {"$group": {"_id": "$patient_key", "count": {"$sum": 1}}},
            {"$count": "total"}
        ]
        prev30_patients_pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": prev30_start, "$lt": prev30_end}
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {"$group": {"_id": "$patient_key", "count": {"$sum": 1}}},
            {"$count": "total"}
        ]

        # Casos últimos 30 días (conteo total)
        last30_cases_pipeline = [
            {"$match": {"created_at": {"$gte": last30_start, "$lt": now}}},
            {"$count": "total"}
        ]
        prev30_cases_pipeline = [
            {"$match": {"created_at": {"$gte": prev30_start, "$lt": prev30_end}}},
            {"$count": "total"}
        ]

        last30_patients_result = await self.collection.aggregate(last30_patients_pipeline).to_list(1)
        prev30_patients_result = await self.collection.aggregate(prev30_patients_pipeline).to_list(1)
        last30_cases_result = await self.collection.aggregate(last30_cases_pipeline).to_list(1)
        prev30_cases_result = await self.collection.aggregate(prev30_cases_pipeline).to_list(1)

        pacientes_last30 = last30_patients_result[0]["total"] if last30_patients_result else 0
        pacientes_prev30 = prev30_patients_result[0]["total"] if prev30_patients_result else 0
        casos_last30 = last30_cases_result[0]["total"] if last30_cases_result else 0
        casos_prev30 = prev30_cases_result[0]["total"] if prev30_cases_result else 0

        if pacientes_prev30 > 0:
            pacientes_cambio = ((pacientes_last30 - pacientes_prev30) / pacientes_prev30) * 100
        else:
            pacientes_cambio = 100.0 if pacientes_last30 > 0 else 0.0
        
        if casos_prev30 > 0:
            casos_cambio = ((casos_last30 - casos_prev30) / casos_prev30) * 100
        else:
            casos_cambio = 100.0 if casos_last30 > 0 else 0.0
        
        return {
            "pacientes": {
                "mes_actual": pacientes_mes_actual,
                "mes_anterior": pacientes_mes_anterior,
                "cambio_porcentual": round(pacientes_cambio, 2)
            },
            "casos": {
                "mes_actual": casos_mes_actual,
                "mes_anterior": casos_mes_anterior,
                "cambio_porcentual": round(casos_cambio, 2)
            }
        }

    async def get_metrics_pathologist(self, pathologist_code: str) -> Dict[str, Any]:
        """Obtener métricas específicas de un patólogo"""
        now = datetime.now()
        current_month_start = datetime(now.year, now.month, 1)
        
        # Mes anterior
        if now.month == 1:
            previous_month_start = datetime(now.year - 1, 12, 1)
        else:
            previous_month_start = datetime(now.year, now.month - 1, 1)
        
        # Próximo mes para el rango
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1)
        
        # Pipeline para pacientes del patólogo en el mes actual
        current_month_patients_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": current_month_start,
                        "$lt": next_month_start
                    },
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {
                "$group": {
                    "_id": "$patient_key",
                    "count": {"$sum": 1}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para pacientes del patólogo en el mes anterior
        previous_month_patients_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": previous_month_start,
                        "$lt": current_month_start
                    },
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {
                "$group": {
                    "_id": "$patient_key",
                    "count": {"$sum": 1}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para casos del patólogo en el mes actual
        current_month_cases_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": current_month_start,
                        "$lt": next_month_start
                    },
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Pipeline para casos del patólogo en el mes anterior
        previous_month_cases_pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": previous_month_start,
                        "$lt": current_month_start
                    },
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {
                "$count": "total"
            }
        ]
        
        # Ejecutar agregaciones
        current_month_patients_result = await self.collection.aggregate(current_month_patients_pipeline).to_list(1)
        previous_month_patients_result = await self.collection.aggregate(previous_month_patients_pipeline).to_list(1)
        current_month_cases_result = await self.collection.aggregate(current_month_cases_pipeline).to_list(1)
        previous_month_cases_result = await self.collection.aggregate(previous_month_cases_pipeline).to_list(1)
        
        # Procesar resultados
        pacientes_mes_actual = current_month_patients_result[0]["total"] if current_month_patients_result else 0
        pacientes_mes_anterior = previous_month_patients_result[0]["total"] if previous_month_patients_result else 0
        casos_mes_actual = current_month_cases_result[0]["total"] if current_month_cases_result else 0
        casos_mes_anterior = previous_month_cases_result[0]["total"] if previous_month_cases_result else 0
        
        # Calcular cambios porcentuales con ventanas rodantes de 30 días (filtrando por patólogo)
        from datetime import timedelta
        last30_start = now - timedelta(days=30)
        prev30_start = now - timedelta(days=60)
        prev30_end = last30_start

        last30_patients_pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": last30_start, "$lt": now},
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {"$group": {"_id": "$patient_key", "count": {"$sum": 1}}},
            {"$count": "total"}
        ]
        prev30_patients_pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": prev30_start, "$lt": prev30_end},
                    "assigned_pathologist.id": pathologist_code
                }
            },
            {"$addFields": {"patient_key": {"$ifNull": ["$patient_info.patient_code", {"$cond": [{"$and": [{"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_type", ""]}}, 0]}, {"$gt": [{"$strLenCP": {"$ifNull": ["$patient_info.identification_number", ""]}}, 0]}]}, {"$concat": ["$patient_info.identification_type", "-", "$patient_info.identification_number"]}, "$patient_info.identification_number"]}]}}},
            {"$group": {"_id": "$patient_key", "count": {"$sum": 1}}},
            {"$count": "total"}
        ]

        last30_cases_pipeline = [
            {"$match": {"created_at": {"$gte": last30_start, "$lt": now}, "assigned_pathologist.id": pathologist_code}},
            {"$count": "total"}
        ]
        prev30_cases_pipeline = [
            {"$match": {"created_at": {"$gte": prev30_start, "$lt": prev30_end}, "assigned_pathologist.id": pathologist_code}},
            {"$count": "total"}
        ]

        last30_patients_result = await self.collection.aggregate(last30_patients_pipeline).to_list(1)
        prev30_patients_result = await self.collection.aggregate(prev30_patients_pipeline).to_list(1)
        last30_cases_result = await self.collection.aggregate(last30_cases_pipeline).to_list(1)
        prev30_cases_result = await self.collection.aggregate(prev30_cases_pipeline).to_list(1)

        pacientes_last30 = last30_patients_result[0]["total"] if last30_patients_result else 0
        pacientes_prev30 = prev30_patients_result[0]["total"] if prev30_patients_result else 0
        casos_last30 = last30_cases_result[0]["total"] if last30_cases_result else 0
        casos_prev30 = prev30_cases_result[0]["total"] if prev30_cases_result else 0

        if pacientes_prev30 > 0:
            pacientes_cambio = ((pacientes_last30 - pacientes_prev30) / pacientes_prev30) * 100
        else:
            pacientes_cambio = 100.0 if pacientes_last30 > 0 else 0.0
        
        if casos_prev30 > 0:
            casos_cambio = ((casos_last30 - casos_prev30) / casos_prev30) * 100
        else:
            casos_cambio = 100.0 if casos_last30 > 0 else 0.0
        
        return {
            "pacientes": {
                "mes_actual": pacientes_mes_actual,
                "mes_anterior": pacientes_mes_anterior,
                "cambio_porcentual": round(pacientes_cambio, 2)
            },
            "casos": {
                "mes_actual": casos_mes_actual,
                "mes_anterior": casos_mes_anterior,
                "cambio_porcentual": round(casos_cambio, 2)
            }
        }
