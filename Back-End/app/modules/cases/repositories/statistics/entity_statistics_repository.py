from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class EntityStatisticsRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.cases

    # Rendimiento mensual por entidad (solo casos completados).
    async def get_monthly_entity_performance(
        self,
        month: int,
        year: int,
        entity_name: str = None
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date},
            "patient_info.entity_info.name": {"$exists": True, "$ne": None, "$ne": ""}
        }
        if entity_name:
            match_conditions["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
        pipeline = [
            {"$match": match_conditions},
            {
                "$group": {
                    "_id": {
                        "entity_name": "$patient_info.entity_info.name",
                        "entity_code": "$patient_info.entity_info.id"
                    },
                    "total_cases": {"$sum": 1},
                    "ambulatorios": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$patient_info.care_type", "Ambulatorio"]},
                                1,
                                0
                            ]
                        }
                    },
                    "hospitalizados": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$patient_info.care_type", "Hospitalizado"]},
                                1,
                                0
                            ]
                        }
                    },
                    "total_business_days": {"$sum": "$business_days"},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$_id.entity_name",
                    "codigo": "$_id.entity_code",
                    "ambulatorios": 1,
                    "hospitalizados": 1,
                    "total": "$total_cases",
                    "avg_business_days": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        total_ambulatorios = sum(entity["ambulatorios"] for entity in results)
        total_hospitalizados = sum(entity["hospitalizados"] for entity in results)
        total_cases = sum(entity["total"] for entity in results)
        weighted_days = sum(entity["avg_business_days"] * entity["total"] for entity in results)
        tiempo_promedio = weighted_days / total_cases if total_cases > 0 else 0
        
        summary = {
            "total": total_cases,
            "ambulatorios": total_ambulatorios,
            "hospitalizados": total_hospitalizados,
            "tiempoPromedio": round(tiempo_promedio, 2)
        }
        
        return {"entities": results, "summary": summary}

    # Detalle estadístico de una entidad en el mes.
    async def get_entity_details(
        self,
        entity_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        match_conditions = {
            "patient_info.entity_info.name": {"$regex": entity_name.strip(), "$options": "i"},
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date}
        }
        basic_stats_pipeline = [
            {"$match": match_conditions},
            {
                "$group": {
                    "_id": None,
                    "total_pacientes": {"$sum": 1},
                    "ambulatorios": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$patient_info.care_type", "Ambulatorio"]},
                                1,
                                0
                            ]
                        }
                    },
                    "hospitalizados": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$patient_info.care_type", "Hospitalizado"]},
                                1,
                                0
                            ]
                        }
                    },
                    "total_samples": {"$sum": {"$size": {"$ifNull": ["$samples", []]}}},
                    "business_days_stats": {
                        "$push": "$business_days"
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total_pacientes": 1,
                    "ambulatorios": 1,
                    "hospitalizados": 1,
                    "promedio_muestras_por_paciente": {
                        "$cond": [
                            {"$gt": ["$total_pacientes", 0]},
                            {"$round": [{"$divide": ["$total_samples", "$total_pacientes"]}, 2]},
                            0
                        ]
                    }
                }
            }
        ]
        
        basic_stats = await self.collection.aggregate(basic_stats_pipeline).to_list(length=None)
        basic_stats = basic_stats[0] if basic_stats else {
            "total_pacientes": 0,
            "ambulatorios": 0,
            "hospitalizados": 0,
            "promedio_muestras_por_paciente": 0
        }
        business_days_pipeline = [
            {"$match": match_conditions},
            {
                "$group": {
                    "_id": None,
                    "minimo_dias": {"$min": "$business_days"},
                    "maximo_dias": {"$max": "$business_days"},
                    "promedio_dias": {"$avg": "$business_days"},
                    "muestras_completadas": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "minimo_dias": 1,
                    "maximo_dias": 1,
                    "promedio_dias": {"$round": ["$promedio_dias", 2]},
                    "muestras_completadas": 1
                }
            }
        ]
        
        business_days_stats = await self.collection.aggregate(business_days_pipeline).to_list(length=None)
        business_days_stats = business_days_stats[0] if business_days_stats else {
            "minimo_dias": 0,
            "maximo_dias": 0,
            "promedio_dias": 0,
            "muestras_completadas": 0
        }
        tests_pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$group": {
                    "_id": {
                        "test_code": "$samples.tests.id",
                        "test_name": "$samples.tests.name"
                    },
                    "total_solicitudes": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.test_code",
                    "nombre": "$_id.test_name",
                    "total_solicitudes": 1
                }
            },
            {"$sort": {"total_solicitudes": -1}},
            {"$limit": 10}
        ]
        
        tests_results = await self.collection.aggregate(tests_pipeline).to_list(length=None)
        return {
            "detalles": {
                "estadisticas_basicas": basic_stats,
                "tiempos_procesamiento": business_days_stats,
                "pruebas_mas_solicitadas": tests_results
            }
        }
    
    async def get_entity_pathologists(
        self,
        entity_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get pathologists who work with a specific entity"""
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "patient_info.entity_info.name": {"$regex": entity_name.strip(), "$options": "i"},
                    "state": "Completado",
                    "signed_at": {"$gte": start_date, "$lt": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "pathologist_code": "$assigned_pathologist.id",
                        "pathologist_name": "$assigned_pathologist.name"
                    },
                    "total_casos": {"$sum": 1},
                    "casos_completados": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$state", "Completado"]},
                                1,
                                0
                            ]
                        }
                    },
                    "total_business_days": {"$sum": "$business_days"},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.pathologist_code",
                    "nombre": "$_id.pathologist_name",
                    "total_casos": 1,
                    "casos_completados": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total_casos": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"patologos": results}
    
    async def debug_unique_entities(self, month: int, year: int) -> Dict[str, Any]:
        """Debug method to see all unique entities in cases"""
        from datetime import datetime
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Simple pipeline to get all unique entities
        pipeline = [
            {
                "$match": {
                    "state": "Completado",
                    "signed_at": {"$gte": start_date, "$lt": end_date},
                    "patient_info.entity_info.name": {"$exists": True, "$ne": None, "$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": {
                        "entity_name": "$patient_info.entity_info.name",
                        "entity_code": "$patient_info.entity_info.id"
                    },
                    "total_cases": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$_id.entity_name",
                    "codigo": "$_id.entity_code",
                    "total_cases": 1
                }
            },
            {"$sort": {"total_cases": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        
        return {
            "total_unique_entities": len(results),
            "entities": results,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def debug_all_entities_in_cases(self, month: int, year: int) -> Dict[str, Any]:
        """Debug method to see ALL entities that have cases (any state) in the date range"""
        from datetime import datetime
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Pipeline to get ALL entities with cases (any state)
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lt": end_date},
                    "patient_info.entity_info.name": {"$exists": True, "$ne": None, "$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": {
                        "entity_name": "$patient_info.entity_info.name",
                        "entity_code": "$patient_info.entity_info.id"
                    },
                    "total_cases": {"$sum": 1},
                    "completed_cases": {
                        "$sum": {
                            "$cond": [{"$eq": ["$state", "Completado"]}, 1, 0]
                        }
                    },
                    "states": {"$addToSet": "$state"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$_id.entity_name",
                    "codigo": "$_id.entity_code",
                    "total_cases": 1,
                    "completed_cases": 1,
                    "states": 1
                }
            },
            {"$sort": {"total_cases": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        
        return {
            "total_entities_with_cases": len(results),
            "entities": results,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }