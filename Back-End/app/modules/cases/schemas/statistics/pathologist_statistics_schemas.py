from typing import List
from pydantic import BaseModel, Field


class PathologistPerformanceItem(BaseModel):
    """Rendimiento mensual por patólogo"""
    code: str = Field(..., description="Código del patólogo")
    name: str = Field(..., description="Nombre del patólogo")
    withinOpportunity: int = Field(..., description="Casos dentro de oportunidad")
    outOfOpportunity: int = Field(..., description="Casos fuera de oportunidad")
    averageDays: float = Field(..., description="Promedio de días hábiles")


class PathologistMonthlyPerformanceResponse(BaseModel):
    """Respuesta de rendimiento mensual de patólogos"""
    pathologists: List[PathologistPerformanceItem] = Field(..., description="Listado de patólogos con métricas")

    class Config:
        from_attributes = True


class PathologistEntityItem(BaseModel):
    """Entidades asociadas a un patólogo"""
    name: str = Field(..., description="Nombre de la entidad")
    codigo: str = Field(..., description="Código de la entidad")
    type: str = Field(..., description="Tipo de entidad")
    casesCount: int = Field(..., description="Total de casos del patólogo en la entidad")


class PathologistEntitiesResponse(BaseModel):
    """Respuesta de entidades por patólogo"""
    entidades: List[PathologistEntityItem] = Field(..., description="Listado de entidades")

    class Config:
        from_attributes = True


class PathologistTestItem(BaseModel):
    """Pruebas asociadas a un patólogo"""
    name: str = Field(..., description="Nombre de la prueba")
    codigo: str = Field(..., description="Código de la prueba")
    category: str = Field(..., description="Categoría de la prueba")
    count: int = Field(..., description="Total de pruebas realizadas")


class PathologistTestsResponse(BaseModel):
    """Respuesta de pruebas por patólogo"""
    pruebas: List[PathologistTestItem] = Field(..., description="Listado de pruebas")

    class Config:
        from_attributes = True


class PathologistOpportunitySummary(BaseModel):
    """Resumen de oportunidad de un patólogo"""
    total: int = Field(..., description="Total de casos")
    within: int = Field(..., description="Casos dentro de oportunidad")
    out: int = Field(..., description="Casos fuera de oportunidad")
    averageDays: float = Field(..., description="Promedio de días hábiles")


class PathologistMonthlyTrendItem(BaseModel):
    """Tendencia mensual de un patólogo"""
    month: int = Field(..., description="Mes (1-12)")
    year: int = Field(..., description="Año")
    total: int = Field(..., description="Total de casos del mes")
    within: int = Field(..., description="Casos dentro de oportunidad")
    out: int = Field(..., description="Casos fuera de oportunidad")
    averageDays: float = Field(..., description="Promedio de días hábiles del mes")


class PathologistMonthlyTrendsResponse(BaseModel):
    """Respuesta de tendencias mensuales de un patólogo"""
    monthlyTrends: List[PathologistMonthlyTrendItem] = Field(..., description="Serie mensual de métricas")

    class Config:
        from_attributes = True
