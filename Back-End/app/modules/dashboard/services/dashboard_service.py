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
        """Obtener estadísticas de casos de un patólogo específico"""
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        
        # Mes anterior al anterior
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        # Filtro para casos del patólogo
        filtro_patologo = {"patologo_asignado.codigo": patologo_code}
        
        # Casos del mes actual
        casos_mes_actual = await self.caso_repository.collection.count_documents({
            **filtro_patologo,
            "fecha_creacion": {"$gte": inicio_mes_actual}
        })
        
        # Casos del mes anterior
        casos_mes_anterior = await self.caso_repository.collection.count_documents({
            **filtro_patologo,
            "fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}
        })
        
        # Casos del mes anterior al anterior
        casos_mes_anterior_anterior = await self.caso_repository.collection.count_documents({
            **filtro_patologo,
            "fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}
        })
        
        # Calcular cambio porcentual (mes anterior vs mes anterior al anterior)
        cambio_porcentual = 0.0
        if casos_mes_anterior_anterior > 0:
            cambio_porcentual = round(((casos_mes_anterior - casos_mes_anterior_anterior) / casos_mes_anterior_anterior) * 100, 2)
        elif casos_mes_anterior > 0:
            cambio_porcentual = 100.0
        
        return {
            "mes_actual": casos_mes_actual,
            "mes_anterior": casos_mes_anterior,
            "cambio_porcentual": cambio_porcentual
        }
    
    async def _get_estadisticas_pacientes_patologo(self, patologo_code: str) -> Dict[str, Any]:
        """Obtener estadísticas de pacientes que tienen casos asignados al patólogo"""
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        
        # Mes anterior al anterior
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        # Obtener pacientes únicos del mes actual que tienen casos asignados al patólogo
        pipeline_pacientes_actual = [
            {
                "$match": {
                    "patologo_asignado.codigo": patologo_code,
                    "fecha_creacion": {"$gte": inicio_mes_actual}
                }
            },
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]
        
        # Obtener pacientes únicos del mes anterior que tienen casos asignados al patólogo
        pipeline_pacientes_anterior = [
            {
                "$match": {
                    "patologo_asignado.codigo": patologo_code,
                    "fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}
                }
            },
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]
        
        # Obtener pacientes únicos del mes anterior al anterior que tienen casos asignados al patólogo
        pipeline_pacientes_anterior_anterior = [
            {
                "$match": {
                    "patologo_asignado.codigo": patologo_code,
                    "fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}
                }
            },
            {"$group": {"_id": "$paciente.paciente_code"}},
            {"$count": "total"}
        ]
        
        # Ejecutar consultas
        resultado_actual = await self.caso_repository.collection.aggregate(pipeline_pacientes_actual).to_list(length=None)
        resultado_anterior = await self.caso_repository.collection.aggregate(pipeline_pacientes_anterior).to_list(length=None)
        resultado_anterior_anterior = await self.caso_repository.collection.aggregate(pipeline_pacientes_anterior_anterior).to_list(length=None)
        
        pacientes_mes_actual = resultado_actual[0]["total"] if resultado_actual else 0
        pacientes_mes_anterior = resultado_anterior[0]["total"] if resultado_anterior else 0
        pacientes_mes_anterior_anterior = resultado_anterior_anterior[0]["total"] if resultado_anterior_anterior else 0
        
        # Calcular cambio porcentual (mes anterior vs mes anterior al anterior)
        cambio_porcentual = 0.0
        if pacientes_mes_anterior_anterior > 0:
            cambio_porcentual = round(((pacientes_mes_anterior - pacientes_mes_anterior_anterior) / pacientes_mes_anterior_anterior) * 100, 2)
        elif pacientes_mes_anterior > 0:
            cambio_porcentual = 100.0
        
        return {
            "mes_actual": pacientes_mes_actual,
            "mes_anterior": pacientes_mes_anterior,
            "cambio_porcentual": cambio_porcentual
        }
