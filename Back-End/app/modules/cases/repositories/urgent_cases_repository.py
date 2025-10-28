"""
Repositorio de casos urgentes: agrega métricas y lista casos según días en sistema.
"""
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class UrgentCasesRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.cases

    # Retorna casos en estados críticos con días en sistema >= min_days.
    async def find_urgent_cases(
        self,
        limit: int = 50,
        min_days: int = 6,
        pathologist_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        match_stage: Dict[str, Any] = {
            "state": {"$in": ["En proceso", "Por firmar"]},
        }
        if pathologist_code:
            match_stage["assigned_pathologist.id"] = pathologist_code

        # Pipeline: calcula días en sistema, agrupa y proyecta campos clave.
        pipeline: List[Dict[str, Any]] = [
            {"$match": match_stage},
            {
                "$addFields": {
                    "days_in_system": {
                        "$dateDiff": {
                            "startDate": "$created_at",
                            "endDate": "$$NOW",
                            "unit": "day",
                        }
                    }
                }
            },
            {"$match": {"days_in_system": {"$gte": int(min_days)}}},
            {"$unwind": {"path": "$samples", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$samples.tests", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": "$case_code",
                    "doc": {"$first": "$$ROOT"},
                    "tests_list": {
                        "$addToSet": {
                            "$cond": [
                                {"$ifNull": ["$samples.tests.id", False]},
                                {"$concat": [
                                    {"$toString": "$samples.tests.id"},
                                    " - ",
                                    {"$ifNull": ["$samples.tests.name", ""]}
                                ]},
                                None
                            ]
                        }
                    }
                }
            },
            {
                "$project": {
                    "doc": 1,
                    "tests_list": {
                        "$filter": {
                            "input": "$tests_list",
                            "as": "t",
                            "cond": {"$ne": ["$$t", None]},
                        }
                    }
                }
            },
            {"$sort": {"doc.days_in_system": -1, "doc.created_at": 1}},
            {"$limit": int(limit)},
            {
                "$project": {
                    "_id": 0,
                    "case_code": "$_id",
                    "patient_name": "$doc.patient_info.name",
                    "patient_code": {
                        "$ifNull": [
                            "$doc.patient_info.patient_code",
                            {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$doc.patient_info.identification_type", ""]}}, 0]},
                                            {"$gt": [{"$strLenCP": {"$ifNull": ["$doc.patient_info.identification_number", ""]}}, 0]}
                                        ]
                                    },
                                    {"$concat": ["$doc.patient_info.identification_type", "-", "$doc.patient_info.identification_number"]},
                                    "$doc.patient_info.identification_number"
                                ]
                            }
                        ]
                    },
                    "entity_name": "$doc.patient_info.entity_info.name",
                    "tests": "$tests_list",
                    "pathologist_name": "$doc.assigned_pathologist.name",
                    "created_at": "$doc.created_at",
                    "state": "$doc.state",
                    "priority": "$doc.priority",
                    "days_in_system": "$doc.days_in_system"
                }
            }
        ]

        return await self.collection.aggregate(pipeline).to_list(length=limit)


