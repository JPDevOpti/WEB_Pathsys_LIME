from typing import Dict, Any, Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class TestStatisticsRepository:
    # Repositorio para estadísticas de pruebas (rendimiento y oportunidad)
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.cases
    
    def _get_entity_filter_pattern(self, entity_name: str) -> str:
        # Devuelve patrón regex para filtrar entidades (soporta abreviaturas)
        if not entity_name or not entity_name.strip():
            return ""
        
        entity_name = entity_name.strip()
        abbreviation_mappings = {
            'HAMA': r'Hospital Alma Máter de Antioquia',
            'HGM': r'Hospital General de Medellín Luz Castro G\.',
            'HUSVP': r'Hospital Universitario San Vicente de Paul',
            'CES': r'Clínica CES',
            'VID': r'Clínica VID - Fundación Santa María',
            'SURA': r'SURA',
            'PROLAB': r'PROLAB S\.A\.S',
            'LIME': r'LIME',
            'TEM': r'TEM - SIU',
            'INVESTIGACION': r'Investigación',
            'MICROBIOLOGIA': r'Microbiología',
            'PATOLOGIA': r'Patología',
            'SUESCUN': r'Patología Suescún S\.A\.S',
            'INTEGRAL': r'Patología Integral S\.A',
            'HSVF': r'Centros Especializados HSVF Rionegro',
            'RENALES': r'Renales IPS Clínica León XIII',
            'AMBULATORIOS': r'Hospitales Ambulatorios',
            'CARDIOLOGICA': r'Clínica Cardiovascular Santa María',
            'NEUROCENTRO': r'Neurocentro - Pereira',
            'IPS': r'IPS Universitaria Ambulatoria',
            'HOSPITAL': r'Hospital',
            'CLINICA': r'Clínica'
        }
        
        if entity_name.upper() in abbreviation_mappings:
            return abbreviation_mappings[entity_name.upper()]
        return f".*{entity_name}.*"
    
    async def get_monthly_test_performance(
        self, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # Rendimiento mensual de pruebas: solicitadas, completadas y tiempos promedio
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        match_conditions = {
            "created_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests": {"$exists": True, "$ne": []}
        }
        if entity_name:
            entity_pattern = self._get_entity_filter_pattern(entity_name)
            if entity_pattern:
                match_conditions["patient_info.entity_info.name"] = {"$regex": entity_pattern, "$options": "i"}
        pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$lookup": {
                    "from": "tests",
                    "localField": "samples.tests.id",
                    "foreignField": "test_code",
                    "as": "test_info"
                }
            },
            {"$unwind": {"path": "$test_info", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": {
                        "test_code": "$samples.tests.id"
                    },
                    "test_name": {"$first": "$test_info.name"},
                    "total_solicitadas": {"$sum": 1},
                    "total_completadas": {
                        "$sum": {
                            "$cond": [{"$eq": ["$state", "Completado"]}, 1, 0]
                        }
                    },
                    "total_business_days": {"$sum": {"$ifNull": ["$business_days", 0]}},
                    "avg_business_days": {"$avg": {"$ifNull": ["$business_days", 0]}}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.test_code",
                    "nombre": {"$ifNull": ["$test_name", "$_id.test_code"]},
                    "solicitadas": "$total_solicitadas",
                    "completadas": "$total_completadas",
                    "tiempoPromedio": {"$round": ["$avg_business_days", 2]},
                    "porcentajeCompletado": {
                        "$round": [
                            {"$multiply": [{"$divide": ["$total_completadas", "$total_solicitadas"]}, 100]}, 
                            2
                        ]
                    }
                }
            },
            {"$sort": {"solicitadas": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        total_solicitadas = sum(test["solicitadas"] for test in results)
        total_completadas = sum(test["completadas"] for test in results)
        if total_solicitadas > 0:
            weighted_avg_days = sum(test["solicitadas"] * test["tiempoPromedio"] for test in results) / total_solicitadas
        else:
            weighted_avg_days = 0
        
        return {
            "tests": results,
            "summary": {
                "totalSolicitadas": total_solicitadas,
                "totalCompletadas": total_completadas,
                "tiempoPromedio": round(weighted_avg_days, 2)
            }
        }
    
    async def get_test_details(
        self, 
        test_code: str, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        match_conditions = {
            "created_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests.id": test_code
        }
        if entity_name:
            entity_pattern = self._get_entity_filter_pattern(entity_name)
            if entity_pattern:
                match_conditions["patient_info.entity_info.name"] = {"$regex": entity_pattern, "$options": "i"}
        basic_stats_pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {"$match": {"samples.tests.id": test_code}},
            {
                "$group": {
                    "_id": None,
                    "total_solicitadas": {"$sum": 1},
                    "total_completadas": {
                        "$sum": {
                            "$cond": [{"$eq": ["$state", "Completado"]}, 1, 0]
                        }
                    },
                    "total_business_days": {"$sum": {"$ifNull": ["$business_days", 0]}},
                    "avg_business_days": {"$avg": {"$ifNull": ["$business_days", 0]}}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total_solicitadas": 1,
                    "total_completadas": 1,
                    "porcentaje_completado": {
                        "$round": [
                            {"$multiply": [{"$divide": ["$total_completadas", "$total_solicitadas"]}, 100]}, 
                            2
                        ]
                    },
                    "promedio_dias": {"$round": ["$avg_business_days", 2]}
                }
            }
        ]
        
        basic_stats_result = await self.collection.aggregate(basic_stats_pipeline).to_list(length=1)
        basic_stats = basic_stats_result[0] if basic_stats_result else {
            "total_solicitadas": 0,
            "total_completadas": 0,
            "porcentaje_completado": 0,
            "promedio_dias": 0
        }
        opportunity_pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {"$match": {"samples.tests.id": test_code}},
            {
                "$group": {
                    "_id": None,
                    "dentro_oportunidad": {
                        "$sum": {
                            "$cond": [{"$lte": ["$business_days", 7]}, 1, 0]
                        }
                    },
                    "fuera_oportunidad": {
                        "$sum": {
                            "$cond": [{"$gt": ["$business_days", 7]}, 1, 0]
                        }
                    },
                    "total_casos": {"$sum": 1}
                }
            }
        ]
        
        opportunity_result = await self.collection.aggregate(opportunity_pipeline).to_list(length=1)
        opportunity_stats = opportunity_result[0] if opportunity_result else {
            "dentro_oportunidad": 0,
            "fuera_oportunidad": 0,
            "total_casos": 0
        }
        
        # Get pathologists who worked on this test
        pathologists_pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {"$match": {"samples.tests.id": test_code}},
            {
                "$group": {
                    "_id": {
                        "pathologist_name": "$assigned_pathologist.name",
                        "pathologist_code": "$assigned_pathologist.id"
                    },
                    "total_procesadas": {"$sum": 1},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$_id.pathologist_name",
                    "codigo": "$_id.pathologist_code",
                    "total_procesadas": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total_procesadas": -1}}
        ]
        
        pathologists_result = await self.collection.aggregate(pathologists_pipeline).to_list(length=1000)
        
        return {
            "estadisticas_principales": {
                "total_solicitadas": basic_stats["total_solicitadas"],
                "total_completadas": basic_stats["total_completadas"],
                "porcentaje_completado": basic_stats["porcentaje_completado"]
            },
            "tiempos_procesamiento": {
                "promedio_dias": basic_stats["promedio_dias"],
                "dentro_oportunidad": opportunity_stats["dentro_oportunidad"],
                "fuera_oportunidad": opportunity_stats["fuera_oportunidad"],
                "total_casos": opportunity_stats["total_casos"]
            },
            "patologos": pathologists_result
        }
    
    async def get_test_pathologists(
        self, 
        test_code: str, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Lista de patólogos que procesaron una prueba específica
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions - Include all cases, not just completed ones
        match_conditions = {
            "created_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests.id": test_code
        }
        
        # Add entity filter if specified - support partial matching for abbreviated names
        if entity_name:
            entity_pattern = self._get_entity_filter_pattern(entity_name)
            if entity_pattern:
                match_conditions["patient_info.entity_info.name"] = {"$regex": entity_pattern, "$options": "i"}
        
        pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {"$match": {"samples.tests.id": test_code}},
            {
                "$group": {
                    "_id": {
                        "pathologist_name": "$assigned_pathologist.name",
                        "pathologist_code": "$assigned_pathologist.id"
                    },
                    "total_procesadas": {"$sum": 1},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "nombre": "$_id.pathologist_name",
                    "codigo": "$_id.pathologist_code",
                    "total_procesadas": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total_procesadas": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        return results
    
    async def get_test_opportunity_summary(
        self, 
        month: int, 
        year: int, 
        threshold_days: int = 7,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # Resumen de oportunidad para pruebas (dentro/fuera y porcentaje)
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions - Include all cases, not just completed ones
        match_conditions = {
            "created_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests": {"$exists": True, "$ne": []}
        }
        
        # Add entity filter if specified - support partial matching for abbreviated names
        if entity_name:
            entity_pattern = self._get_entity_filter_pattern(entity_name)
            if entity_pattern:
                match_conditions["patient_info.entity_info.name"] = {"$regex": entity_pattern, "$options": "i"}
        
        pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$group": {
                    "_id": {
                        "test_code": "$samples.tests.id",
                        "test_name": "$samples.tests.name"
                    },
                    "total_casos": {"$sum": 1},
                    "dentro_oportunidad": {
                        "$sum": {
                            "$cond": [{"$lte": ["$business_days", threshold_days]}, 1, 0]
                        }
                    },
                    "fuera_oportunidad": {
                        "$sum": {
                            "$cond": [{"$gt": ["$business_days", threshold_days]}, 1, 0]
                        }
                    },
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.test_code",
                    "nombre": "$_id.test_name",
                    "total_casos": 1,
                    "dentro_oportunidad": 1,
                    "fuera_oportunidad": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]},
                    "porcentaje_oportunidad": {
                        "$round": [
                            {"$multiply": [{"$divide": ["$dentro_oportunidad", "$total_casos"]}, 100]}, 
                            2
                        ]
                    }
                }
            },
            {"$sort": {"total_casos": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        
        # Calculate summary
        total_casos = sum(test["total_casos"] for test in results)
        total_dentro_oportunidad = sum(test["dentro_oportunidad"] for test in results)
        total_fuera_oportunidad = sum(test["fuera_oportunidad"] for test in results)
        
        return {
            "tests": results,
            "summary": {
                "total_casos": total_casos,
                "dentro_oportunidad": total_dentro_oportunidad,
                "fuera_oportunidad": total_fuera_oportunidad,
                "porcentaje_oportunidad": round((total_dentro_oportunidad / total_casos * 100) if total_casos > 0 else 0, 2)
            }
        }
    

    async def get_test_monthly_trends(
        self, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Tendencias mensuales de pruebas por mes (volumen y tiempos)
        
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    },
                    "samples.tests": {"$exists": True, "$ne": []}
                }
            },
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$signed_at"},
                        "test_code": "$samples.tests.id"
                    },
                    "total_casos": {"$sum": 1},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "mes": "$_id.month",
                    "codigo": "$_id.test_code",
                    "total_casos": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"mes": 1, "total_casos": -1}}
        ]
        
        # Add entity filter if specified - support partial matching for abbreviated names
        if entity_name:
            entity_pattern = self._get_entity_filter_pattern(entity_name)
            if entity_pattern:
                pipeline[0]["$match"]["patient_info.entity_info.name"] = {"$regex": entity_pattern, "$options": "i"}
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        return results