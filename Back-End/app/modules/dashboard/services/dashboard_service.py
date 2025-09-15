"""Servicio para el dashboard"""

from typing import Dict, Any
from datetime import datetime, timedelta
from app.modules.dashboard.schemas.dashboard import DashboardMetrics
from app.modules.casos.repositories.caso_repository import CasoRepository
from app.modules.pacientes.repositories.paciente_repository import PacienteRepository
from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.core.exceptions import NotFoundError
from motor.motor_asyncio import AsyncIOMotorDatabase

class DashboardService:
    """Servicio para lógica de negocio del dashboard"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.caso_repository = CasoRepository(db)
        self.paciente_repository = PacienteRepository(db)
        self.patologo_repository = PatologoRepository(db)
    
    async def get_metricas_dashboard(self) -> DashboardMetrics:
        """Obtener métricas generales del dashboard"""
        # Obtener estadísticas de casos
        casos_stats = await self.caso_repository.get_estadisticas()
        
        # Obtener estadísticas de pacientes
        pacientes_stats = await self.paciente_repository.get_statistics()
        
        return DashboardMetrics(
            pacientes={
                "mes_actual": pacientes_stats["mensuales"]["pacientes_mes_actual"],
                "mes_anterior": pacientes_stats["mensuales"]["pacientes_mes_anterior"],
                "cambio_porcentual": pacientes_stats["mensuales"]["cambio_porcentual"]
            },
            casos={
                "mes_actual": casos_stats.casos_mes_actual,
                "mes_anterior": casos_stats.casos_mes_anterior,
                "cambio_porcentual": casos_stats.cambio_porcentual
            }
        )
    
    async def get_metricas_patologo(self, patologo_email: str) -> DashboardMetrics:
        """Obtener métricas específicas del patólogo"""
        # Buscar patólogo por email
        patologo = await self.patologo_repository.get_by_email(patologo_email)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Obtener estadísticas de casos del patólogo
        casos_stats = await self._get_estadisticas_casos_patologo(patologo.patologo_code)
        
        # Obtener estadísticas de pacientes del patólogo
        pacientes_stats = await self._get_estadisticas_pacientes_patologo(patologo.patologo_code)
        
        return DashboardMetrics(
            pacientes=pacientes_stats,
            casos=casos_stats
        )
    
    async def _get_estadisticas_casos_patologo(self, patologo_code: str) -> Dict[str, Any]:
        """Obtener estadísticas de casos de un patólogo específico (optimizado con $facet)."""
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)

        pipeline = [
            {"$match": {"patologo_asignado.codigo": patologo_code, "fecha_creacion": {"$gte": inicio_mes_anterior_anterior}}},
            {"$facet": {
                "actual": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_actual}}},
                    {"$count": "total"}
                ],
                "anterior": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}}},
                    {"$count": "total"}
                ],
                "ant_ant": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}}},
                    {"$count": "total"}
                ]
            }}
        ]

        result = await self.caso_repository.collection.aggregate(pipeline).to_list(length=1)
        data = result[0] if result else {"actual": [], "anterior": [], "ant_ant": []}
        casos_mes_actual = (data.get("actual") or [{}])[0].get("total", 0)
        casos_mes_anterior = (data.get("anterior") or [{}])[0].get("total", 0)
        casos_mes_anterior_anterior = (data.get("ant_ant") or [{}])[0].get("total", 0)

        cambio_porcentual = 0.0
        if casos_mes_anterior_anterior > 0:
            cambio_porcentual = round(((casos_mes_anterior - casos_mes_anterior_anterior) / casos_mes_anterior_anterior) * 100, 2)
        elif casos_mes_anterior > 0:
            cambio_porcentual = 100.0

        return {"mes_actual": casos_mes_actual, "mes_anterior": casos_mes_anterior, "cambio_porcentual": cambio_porcentual}
    
    async def _get_estadisticas_pacientes_patologo(self, patologo_code: str) -> Dict[str, Any]:
        """Obtener estadísticas de pacientes del patólogo (optimizado con $facet)."""
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)

        pipeline = [
            {"$match": {"patologo_asignado.codigo": patologo_code, "fecha_creacion": {"$gte": inicio_mes_anterior_anterior}}},
            {"$facet": {
                "actual": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_actual}}},
                    {"$group": {"_id": "$paciente.paciente_code"}},
                    {"$count": "total"}
                ],
                "anterior": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}}},
                    {"$group": {"_id": "$paciente.paciente_code"}},
                    {"$count": "total"}
                ],
                "ant_ant": [
                    {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}}},
                    {"$group": {"_id": "$paciente.paciente_code"}},
                    {"$count": "total"}
                ]
            }}
        ]

        result = await self.caso_repository.collection.aggregate(pipeline).to_list(length=1)
        data = result[0] if result else {"actual": [], "anterior": [], "ant_ant": []}
        pacientes_mes_actual = (data.get("actual") or [{}])[0].get("total", 0)
        pacientes_mes_anterior = (data.get("anterior") or [{}])[0].get("total", 0)
        pacientes_mes_anterior_anterior = (data.get("ant_ant") or [{}])[0].get("total", 0)

        cambio_porcentual = 0.0
        if pacientes_mes_anterior_anterior > 0:
            cambio_porcentual = round(((pacientes_mes_anterior - pacientes_mes_anterior_anterior) / pacientes_mes_anterior_anterior) * 100, 2)
        elif pacientes_mes_anterior > 0:
            cambio_porcentual = 100.0

        return {"mes_actual": pacientes_mes_actual, "mes_anterior": pacientes_mes_anterior, "cambio_porcentual": cambio_porcentual}
    
    async def get_casos_por_mes_patologo(self, patologo_email: str, año: int) -> Dict[str, Any]:
        """Obtener casos por mes específicos del patólogo - OPTIMIZADO"""
        # Buscar patólogo por email
        patologo = await self.patologo_repository.get_by_email(patologo_email)
        if not patologo:
            raise NotFoundError("Patólogo no encontrado")
        
        # Pipeline optimizado con proyección temprana y índices
        pipeline = [
            {
                "$match": {
                    "patologo_asignado.codigo": patologo.patologo_code,
                    "fecha_creacion": {
                        "$gte": datetime(año, 1, 1),
                        "$lt": datetime(año + 1, 1, 1)
                    }
                }
            },
            {
                "$project": {
                    "mes": {"$month": "$fecha_creacion"}
                }
            },
            {
                "$group": {
                    "_id": "$mes",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        # Ejecutar agregación con límite de tiempo
        resultados = await self.caso_repository.collection.aggregate(
            pipeline, 
            allowDiskUse=True,  # Permitir uso de disco para agregaciones grandes
            maxTimeMS=10000     # Timeout de 10 segundos
        ).to_list(length=None)
        
        # Crear array de 12 meses inicializado en 0
        casos_por_mes = [0] * 12
        
        # Llenar con los datos obtenidos
        for resultado in resultados:
            mes = resultado["_id"] - 1  # MongoDB devuelve 1-12, necesitamos 0-11
            casos_por_mes[mes] = resultado["count"]
        
        # Calcular total
        total_casos = sum(casos_por_mes)
        
        return {
            "datos": casos_por_mes,
            "total": total_casos,
            "año": año
        }
    
    async def get_casos_por_mes_general(self, año: int) -> Dict[str, Any]:
        """Obtener casos por mes generales del laboratorio - OPTIMIZADO"""
        # Pipeline optimizado para casos generales
        pipeline = [
            {
                "$match": {
                    "fecha_creacion": {
                        "$gte": datetime(año, 1, 1),
                        "$lt": datetime(año + 1, 1, 1)
                    }
                }
            },
            {
                "$project": {
                    "mes": {"$month": "$fecha_creacion"}
                }
            },
            {
                "$group": {
                    "_id": "$mes",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        # Ejecutar agregación con límite de tiempo
        resultados = await self.caso_repository.collection.aggregate(
            pipeline, 
            allowDiskUse=True,
            maxTimeMS=10000
        ).to_list(length=None)
        
        # Crear array de 12 meses inicializado en 0
        casos_por_mes = [0] * 12
        
        # Llenar con los datos obtenidos
        for resultado in resultados:
            mes = resultado["_id"] - 1  # MongoDB devuelve 1-12, necesitamos 0-11
            casos_por_mes[mes] = resultado["count"]
        
        # Calcular total
        total_casos = sum(casos_por_mes)
        
        return {
            "datos": casos_por_mes,
            "total": total_casos,
            "año": año
        }
