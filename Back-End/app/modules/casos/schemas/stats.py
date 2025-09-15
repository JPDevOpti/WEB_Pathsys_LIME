"""Esquemas de estadísticas para el módulo de casos."""

from pydantic import BaseModel
from typing import Optional


class MesActualStats(BaseModel):
    """Estadísticas del mes actual con comparación a meses anteriores."""
    mes_actual: int
    mes_anterior: int
    mes_anterior_anterior: Optional[int] = None
    cambio_porcentual: float


class DashboardMetricsResponse(BaseModel):
    """Respuesta de métricas del dashboard."""
    pacientes: MesActualStats
    casos: MesActualStats


class OpportunityStatsResponse(BaseModel):
    porcentaje_oportunidad: float
    cambio_porcentual: float
    tiempo_promedio: float
    casos_dentro_oportunidad: int
    casos_fuera_oportunidad: int
    total_casos_mes_anterior: int
    mes_anterior: dict

