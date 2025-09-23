from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.casos.repositories.query.base_query_repository import BaseQueryRepository
from app.modules.casos.schemas.query.urgent_cases import UrgentCasesRequest, UrgentCaseRow


class UrgentCasesRepository(BaseQueryRepository):
    """Repositorio para casos urgentes (≥5 días hábiles)"""
    
    async def get_urgent_cases(self, request: UrgentCasesRequest) -> List[UrgentCaseRow]:
        """Obtiene casos urgentes con cálculo de días hábiles en MongoDB"""
        # Pipeline para casos urgentes (≥5 días hábiles, no completados)
        pipeline = [
            {
                "$match": {
                    "estado": {"$ne": "Completado"},
                    # Filtro por patólogo si se especifica
                    **({"patologo_asignado.codigo": request.patologo_codigo} if request.patologo_codigo else {}),
                    # Filtro por estado si se especifica
                    **({"estado": request.estado} if request.estado else {})
                }
            },
            {
                "$addFields": {
                    "dias_habiles_transcurridos": {
                        "$function": {
                            "body": """
                            function(fechaCreacion) {
                                const hoy = new Date();
                                const inicio = new Date(fechaCreacion);
                                let dias = 0;
                                let fecha = new Date(inicio);
                                
                                while (fecha < hoy) {
                                    const diaSemana = fecha.getDay();
                                    if (diaSemana !== 0 && diaSemana !== 6) {
                                        dias++;
                                    }
                                    fecha.setDate(fecha.getDate() + 1);
                                }
                                return dias;
                            }
                            """,
                            "args": ["$fecha_creacion"],
                            "lang": "js"
                        }
                    }
                }
            },
            {
                "$match": {
                    "dias_habiles_transcurridos": {"$gte": 5}
                }
            },
            {
                "$project": {
                    "caso_code": 1,
                    "paciente_nombre": "$paciente.nombre",
                    "paciente_documento": "$paciente.paciente_code",
                    "fecha_creacion": 1,
                    "dias_habiles_transcurridos": 1,
                    "estado": 1,
                    "prioridad": 1,
                    "patologo_nombre": "$patologo_asignado.nombre",
                    "medico_solicitante": 1,
                    "entidad_nombre": "$paciente.entidad_info.nombre",
                    "pruebas": {
                        "$reduce": {
                            "input": "$muestras",
                            "initialValue": [],
                            "in": {
                                "$concatArrays": [
                                    "$$value",
                                    {
                                        "$map": {
                                            "input": "$$this.pruebas",
                                            "as": "prueba",
                                            "in": {
                                                "$concat": [
                                                    "$$prueba.id",
                                                    " - ",
                                                    "$$prueba.nombre"
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$sort": {
                    "dias_habiles_transcurridos": -1,
                    "fecha_creacion": 1
                }
            },
            {"$limit": request.limite}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return [UrgentCaseRow(**doc) for doc in results]