from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


class UrgentCasesRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.cases

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

        pipeline: List[Dict[str, Any]] = [
            {"$match": match_stage},
            {
                "$addFields": {
                    "dias_en_sistema": {
                        "$dateDiff": {
                            "startDate": "$created_at",
                            "endDate": "$$NOW",
                            "unit": "day",
                        }
                    }
                }
            },
            {"$match": {"dias_en_sistema": {"$gte": int(min_days)}}},
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
            {"$sort": {"doc.dias_en_sistema": -1, "doc.created_at": 1}},
            {"$limit": int(limit)},
            {
                "$project": {
                    "_id": 0,
                    "caso_code": "$_id",
                    "paciente_nombre": "$doc.patient_info.name",
                    "paciente_documento": "$doc.patient_info.patient_code",
                    "entidad_nombre": "$doc.patient_info.entity_info.name",
                    "pruebas": "$tests_list",
                    "patologo_nombre": "$doc.assigned_pathologist.name",
                    "fecha_creacion": "$doc.created_at",
                    "estado": "$doc.state",
                    "prioridad": "$doc.priority",
                    "dias_habiles_transcurridos": "$doc.dias_en_sistema"
                }
            }
        ]

        return await self.collection.aggregate(pipeline).to_list(length=limit)


