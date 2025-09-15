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

