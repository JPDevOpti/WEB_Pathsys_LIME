from typing import Dict, Any, Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class TestStatisticsRepository:
    """Repository for test statistics data access using MongoDB aggregation"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.cases
    
    async def get_monthly_test_performance(
        self, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get monthly performance statistics for all tests"""
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests": {"$exists": True, "$ne": []}
        }
        
        # Add entity filter if specified
        if entity_name:
            match_conditions["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
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
                    "total_solicitadas": {"$sum": 1},
                    "total_completadas": {"$sum": 1},  # Already filtered by "Completado"
                    "total_business_days": {"$sum": "$business_days"},
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.test_code",
                    "nombre": "$_id.test_name",
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
        
        # Calculate summary
        total_solicitadas = sum(test["solicitadas"] for test in results)
        total_completadas = sum(test["completadas"] for test in results)
        total_business_days = sum(test["solicitadas"] * test["tiempoPromedio"] for test in results)
        
        # Calculate weighted average
        weighted_avg_days = total_business_days / total_solicitadas if total_solicitadas > 0 else 0
        
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
        """Get detailed statistics for a specific test"""
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests.id": test_code
        }
        
        # Add entity filter if specified
        if entity_name:
            match_conditions["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
        # Get basic statistics
        basic_stats_pipeline = [
            {"$match": match_conditions},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {"$match": {"samples.tests.id": test_code}},
            {
                "$group": {
                    "_id": None,
                    "total_solicitadas": {"$sum": 1},
                    "total_completadas": {"$sum": 1},
                    "total_business_days": {"$sum": "$business_days"},
                    "avg_business_days": {"$avg": "$business_days"}
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
        
        # Get opportunity statistics (assuming 7 days threshold)
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
        """Get pathologists who worked on a specific test"""
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests.id": test_code
        }
        
        # Add entity filter if specified
        if entity_name:
            match_conditions["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
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
        """Get opportunity summary for tests"""
        
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date},
            "samples.tests": {"$exists": True, "$ne": []}
        }
        
        # Add entity filter if specified
        if entity_name:
            match_conditions["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
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
        """Get monthly trends for tests"""
        
        pipeline = [
            {
                "$match": {
                    "state": "Completado",
                    "signed_at": {
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
                        "test_code": "$samples.tests.id",
                        "test_name": "$samples.tests.name"
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
                    "nombre": "$_id.test_name",
                    "total_casos": 1,
                    "tiempo_promedio": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"mes": 1, "total_casos": -1}}
        ]
        
        # Add entity filter if specified
        if entity_name:
            pipeline[0]["$match"]["patient_info.entity_info.name"] = {"$regex": entity_name.strip(), "$options": "i"}
        
        results = await self.collection.aggregate(pipeline).to_list(length=1000)
        return results