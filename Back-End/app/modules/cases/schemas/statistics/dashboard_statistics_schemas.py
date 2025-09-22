# Dashboard Statistics Schemas
from typing import List, Optional
from pydantic import BaseModel, Field


class CasesByMonthResponse(BaseModel):
    """Schema para respuesta de casos por mes"""
    datos: List[int] = Field(..., description="Array de 12 números representando casos por mes")
    total: int = Field(..., description="Total de casos en el año")
    año: int = Field(..., description="Año consultado")
    meses: List[str] = Field(default=[
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ], description="Nombres de los meses")

    class Config:
        from_attributes = True


class CasesByMonthRequest(BaseModel):
    """Schema para request de casos por mes"""
    año: int = Field(..., ge=2020, le=2030, description="Año a consultar")


class PathologistCasesByMonthRequest(BaseModel):
    """Schema para request de casos por mes por patólogo"""
    año: int = Field(..., ge=2020, le=2030, description="Año a consultar")
    pathologist_code: str = Field(..., min_length=1, max_length=50, description="Código del patólogo")


class DashboardOverviewResponse(BaseModel):
    """Schema para respuesta de resumen general del dashboard"""
    total_casos: int = Field(..., description="Total de casos")
    casos_mes_actual: int = Field(..., description="Casos del mes actual")
    casos_mes_anterior: int = Field(..., description="Casos del mes anterior")
    cambio_porcentual: float = Field(..., description="Cambio porcentual respecto al mes anterior")
    casos_por_estado: dict = Field(..., description="Distribución de casos por estado")

    class Config:
        from_attributes = True


class PacientesMetrics(BaseModel):
    """Schema para métricas de pacientes"""
    mes_actual: int = Field(..., description="Pacientes del mes actual")
    mes_anterior: int = Field(..., description="Pacientes del mes anterior")
    cambio_porcentual: float = Field(..., description="Cambio porcentual respecto al mes anterior")


class CasosMetrics(BaseModel):
    """Schema para métricas de casos"""
    mes_actual: int = Field(..., description="Casos del mes actual")
    mes_anterior: int = Field(..., description="Casos del mes anterior")
    cambio_porcentual: float = Field(..., description="Cambio porcentual respecto al mes anterior")


class MetricsResponse(BaseModel):
    """Schema para respuesta de métricas generales"""
    pacientes: PacientesMetrics = Field(..., description="Métricas de pacientes")
    casos: CasosMetrics = Field(..., description="Métricas de casos")

    class Config:
        from_attributes = True


class MesAnterior(BaseModel):
    """Schema para información del mes anterior"""
    nombre: str = Field(..., description="Nombre del mes anterior")
    numero: int = Field(..., description="Número del mes anterior")
    inicio: str = Field(..., description="Inicio ISO del rango del mes anterior")
    fin: str = Field(..., description="Fin ISO del rango del mes anterior")


class OpportunityMetrics(BaseModel):
    """Schema para métricas de oportunidad"""
    porcentaje_oportunidad: float = Field(..., description="Porcentaje de casos dentro de oportunidad")
    cambio_porcentual: float = Field(..., description="Cambio porcentual respecto al mes anterior")
    total_casos_mes_anterior: int = Field(..., description="Total de casos del mes anterior")
    tiempo_promedio: float = Field(..., description="Tiempo promedio de procesamiento en días")
    casos_dentro_oportunidad: int = Field(..., description="Casos dentro del tiempo de oportunidad")
    casos_fuera_oportunidad: int = Field(..., description="Casos fuera del tiempo de oportunidad")
    mes_anterior: MesAnterior = Field(..., description="Información del mes anterior")


class OpportunityResponse(BaseModel):
    """Schema para respuesta de estadísticas de oportunidad"""
    oportunity: OpportunityMetrics = Field(..., description="Métricas de oportunidad")

    class Config:
        from_attributes = True
