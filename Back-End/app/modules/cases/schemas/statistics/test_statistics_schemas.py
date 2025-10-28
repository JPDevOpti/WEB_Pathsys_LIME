from pydantic import BaseModel, Field
from typing import List, Optional


class TestStats(BaseModel):
    """Estadísticas individuales de pruebas"""
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    solicitadas: int = Field(..., description="Total solicitadas")
    completadas: int = Field(..., description="Total completadas")
    tiempoPromedio: float = Field(..., description="Tiempo promedio de procesamiento en días")
    porcentajeCompletado: float = Field(..., description="Porcentaje de completadas")


class TestSummary(BaseModel):
    """Resumen de estadísticas de pruebas"""
    totalSolicitadas: int = Field(..., description="Total de pruebas solicitadas")
    totalCompletadas: int = Field(..., description="Total de pruebas completadas")
    tiempoPromedio: float = Field(..., description="Tiempo promedio de procesamiento en días")


class MonthlyTestPerformanceResponse(BaseModel):
    """Respuesta de rendimiento mensual de pruebas"""
    tests: List[TestStats] = Field(..., description="Listado de estadísticas de pruebas")
    summary: TestSummary = Field(..., description="Resumen de estadísticas")


class TestMainStats(BaseModel):
    """Estadísticas principales de pruebas"""
    total_solicitadas: int = Field(..., description="Total solicitadas")
    total_completadas: int = Field(..., description="Total completadas")
    porcentaje_completado: float = Field(..., description="Porcentaje de completadas")


class TestProcessingTimes(BaseModel):
    """Tiempos de procesamiento de pruebas"""
    promedio_dias: float = Field(..., description="Promedio de días")
    dentro_oportunidad: int = Field(..., description="Dentro de oportunidad")
    fuera_oportunidad: int = Field(..., description="Fuera de oportunidad")
    total_casos: int = Field(..., description="Total de casos")


class TestPathologist(BaseModel):
    """Patólogo trabajando en una prueba"""
    nombre: str = Field(..., description="Nombre del patólogo")
    codigo: str = Field(..., description="Código del patólogo")
    total_procesadas: int = Field(..., description="Total procesadas")
    tiempo_promedio: float = Field(..., description="Tiempo promedio de procesamiento")


class TestDetailsResponse(BaseModel):
    """Respuesta de detalles de una prueba"""
    estadisticas_principales: TestMainStats = Field(..., description="Estadísticas principales")
    tiempos_procesamiento: TestProcessingTimes = Field(..., description="Tiempos de procesamiento")
    patologos: List[TestPathologist] = Field(..., description="Listado de patólogos")


class TestPathologistsResponse(BaseModel):
    """Respuesta de patólogos por prueba"""
    pathologists: List[TestPathologist] = Field(..., description="Listado de patólogos")


class TestOpportunityStats(BaseModel):
    """Estadísticas de oportunidad de pruebas"""
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    total_casos: int = Field(..., description="Total de casos")
    dentro_oportunidad: int = Field(..., description="Dentro de oportunidad")
    fuera_oportunidad: int = Field(..., description="Fuera de oportunidad")
    tiempo_promedio: float = Field(..., description="Tiempo promedio de procesamiento")
    porcentaje_oportunidad: float = Field(..., description="Porcentaje de oportunidad")


class TestOpportunitySummary(BaseModel):
    """Resumen de oportunidad de pruebas"""
    total_casos: int = Field(..., description="Total de casos")
    dentro_oportunidad: int = Field(..., description="Dentro de oportunidad")
    fuera_oportunidad: int = Field(..., description="Fuera de oportunidad")
    porcentaje_oportunidad: float = Field(..., description="Porcentaje de oportunidad")


class TestOpportunityResponse(BaseModel):
    """Respuesta de resumen de oportunidad de pruebas"""
    tests: List[TestOpportunityStats] = Field(..., description="Estadísticas de oportunidad por prueba")
    summary: TestOpportunitySummary = Field(..., description="Resumen de estadísticas")


class TestMonthlyTrend(BaseModel):
    """Tendencias mensuales de pruebas"""
    mes: int = Field(..., description="Mes")
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    total_casos: int = Field(..., description="Total de casos")
    tiempo_promedio: float = Field(..., description="Tiempo promedio de procesamiento")


class TestMonthlyTrendsResponse(BaseModel):
    """Respuesta de tendencias mensuales de pruebas"""
    trends: List[TestMonthlyTrend] = Field(..., description="Tendencias mensuales")