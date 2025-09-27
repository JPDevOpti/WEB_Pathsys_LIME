from typing import Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class PathologistStatisticsRepository:
    """Repository for pathologist-specific statistics and analytics"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database["cases"]
    
    async def get_pathologist_monthly_performance(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        pathologist_name: str = None
    ) -> Dict[str, Any]:
        """Get monthly performance data for pathologists"""
        
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Base match conditions
        match_conditions = {
            "state": "Completado",
            "signed_at": {"$gte": start_date, "$lt": end_date}
        }
        
        # Add pathologist filter if specified
        if pathologist_name:
            match_conditions["assigned_pathologist.name"] = {"$regex": pathologist_name.strip(), "$options": "i"}
        
        pipeline = [
            {"$match": match_conditions},
            {
                "$group": {
                    "_id": {
                        "pathologist_code": "$assigned_pathologist.id",
                        "pathologist_name": "$assigned_pathologist.name"
                    },
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days", threshold_days]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days", threshold_days]},
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
                    "code": "$_id.pathologist_code",
                    "name": "$_id.pathologist_name",
                    "withinOpportunity": "$within_opportunity",
                    "outOfOpportunity": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total_cases": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"pathologists": results}
    
    async def get_pathologist_entities(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get entities where a pathologist works"""
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "assigned_pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"},
                    "state": "Completado",
                    "signed_at": {"$gte": start_date, "$lt": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "entity_name": "$patient_info.entity_info.name",
                        "entity_code": "$patient_info.entity_info.code"
                    },
                    "casesCount": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.entity_name",
                    "codigo": "$_id.entity_code",
                    "type": "Institución",
                    "casesCount": 1
                }
            },
            {"$sort": {"casesCount": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"entidades": results}
    
    async def get_pathologist_tests(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get tests performed by a pathologist"""
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "assigned_pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"},
                    "state": "Completado",
                    "signed_at": {"$gte": start_date, "$lt": end_date}
                }
            },
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$group": {
                    "_id": {
                        "test_code": "$samples.tests.id",
                        "test_name": "$samples.tests.name"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.test_name",
                    "codigo": "$_id.test_code",
                    "category": "Laboratorio",
                    "count": 1
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"pruebas": results}
    
    async def get_pathologist_opportunity_summary(
        self,
        pathologist_name: str,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        """Get opportunity summary for a specific pathologist"""
        
        pipeline = [
            {
                "$match": {
                    "pathologist.name": pathologist_name.strip(),
                    "state": "Completado",
                    "signed_at": {"$exists": True},
                    "business_days": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days", threshold_days]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days", threshold_days]},
                                1,
                                0
                            ]
                        }
                    },
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total": "$total_cases",
                    "within": "$within_opportunity",
                    "out": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return results[0] if results else {"total": 0, "within": 0, "out": 0, "averageDays": 0}
    
    async def get_pathologist_monthly_trends(
        self,
        pathologist_name: str,
        year: int,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        """Get monthly trends for a pathologist throughout the year"""
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "pathologist.name": pathologist_name.strip(),
                    "state": "Completado",
                    "signed_at": {"$gte": start_date, "$lt": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$signed_at"},
                        "year": {"$year": "$signed_at"}
                    },
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days", threshold_days]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days", threshold_days]},
                                1,
                                0
                            ]
                        }
                    },
                    "avg_business_days": {"$avg": "$business_days"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "month": "$_id.month",
                    "year": "$_id.year",
                    "total": "$total_cases",
                    "within": "$within_opportunity",
                    "out": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"month": 1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Fill in missing months with zeros
        monthly_data = []
        for month in range(1, 13):
            month_data = next((item for item in results if item["month"] == month), {
                "month": month,
                "year": year,
                "total": 0,
                "within": 0,
                "out": 0,
                "averageDays": 0
            })
            monthly_data.append(month_data)
        
        return {"monthlyTrends": monthly_data}
