"""Esquemas para el dashboard"""

from pydantic import BaseModel, Field
from typing import Dict, Any

class MetricasMensuales(BaseModel):
    """Esquema para métricas mensuales"""
    mes_actual: int = Field(..., description="Valor del mes actual")
    mes_anterior: int = Field(..., description="Valor del mes anterior")
    cambio_porcentual: float = Field(..., description="Cambio porcentual respecto al mes anterior")

class DashboardMetrics(BaseModel):
    """Esquema para métricas del dashboard"""
    pacientes: MetricasMensuales = Field(..., description="Métricas de pacientes")
    casos: MetricasMensuales = Field(..., description="Métricas de casos")
