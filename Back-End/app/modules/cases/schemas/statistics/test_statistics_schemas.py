from pydantic import BaseModel, Field
from typing import List, Optional


class TestStats(BaseModel):
    """Schema for individual test statistics"""
    codigo: str = Field(..., description="Test code")
    nombre: str = Field(..., description="Test name")
    solicitadas: int = Field(..., description="Total requested")
    completadas: int = Field(..., description="Total completed")
    tiempoPromedio: float = Field(..., description="Average processing time in days")
    porcentajeCompletado: float = Field(..., description="Completion percentage")


class TestSummary(BaseModel):
    """Schema for test summary statistics"""
    totalSolicitadas: int = Field(..., description="Total tests requested")
    totalCompletadas: int = Field(..., description="Total tests completed")
    tiempoPromedio: float = Field(..., description="Average processing time in days")


class MonthlyTestPerformanceResponse(BaseModel):
    """Response schema for monthly test performance"""
    tests: List[TestStats] = Field(..., description="List of test statistics")
    summary: TestSummary = Field(..., description="Summary statistics")


class TestMainStats(BaseModel):
    """Schema for main test statistics"""
    total_solicitadas: int = Field(..., description="Total requested")
    total_completadas: int = Field(..., description="Total completed")
    porcentaje_completado: float = Field(..., description="Completion percentage")


class TestProcessingTimes(BaseModel):
    """Schema for test processing times"""
    promedio_dias: float = Field(..., description="Average days")
    dentro_oportunidad: int = Field(..., description="Within opportunity")
    fuera_oportunidad: int = Field(..., description="Out of opportunity")
    total_casos: int = Field(..., description="Total cases")


class TestPathologist(BaseModel):
    """Schema for pathologist working on a test"""
    nombre: str = Field(..., description="Pathologist name")
    codigo: str = Field(..., description="Pathologist code")
    total_procesadas: int = Field(..., description="Total processed")
    tiempo_promedio: float = Field(..., description="Average processing time")


class TestDetailsResponse(BaseModel):
    """Response schema for test details"""
    estadisticas_principales: TestMainStats = Field(..., description="Main statistics")
    tiempos_procesamiento: TestProcessingTimes = Field(..., description="Processing times")
    patologos: List[TestPathologist] = Field(..., description="Pathologists list")


class TestPathologistsResponse(BaseModel):
    """Response schema for test pathologists"""
    pathologists: List[TestPathologist] = Field(..., description="Pathologists list")


class TestOpportunityStats(BaseModel):
    """Schema for test opportunity statistics"""
    codigo: str = Field(..., description="Test code")
    nombre: str = Field(..., description="Test name")
    total_casos: int = Field(..., description="Total cases")
    dentro_oportunidad: int = Field(..., description="Within opportunity")
    fuera_oportunidad: int = Field(..., description="Out of opportunity")
    tiempo_promedio: float = Field(..., description="Average processing time")
    porcentaje_oportunidad: float = Field(..., description="Opportunity percentage")


class TestOpportunitySummary(BaseModel):
    """Schema for test opportunity summary"""
    total_casos: int = Field(..., description="Total cases")
    dentro_oportunidad: int = Field(..., description="Within opportunity")
    fuera_oportunidad: int = Field(..., description="Out of opportunity")
    porcentaje_oportunidad: float = Field(..., description="Opportunity percentage")


class TestOpportunityResponse(BaseModel):
    """Response schema for test opportunity summary"""
    tests: List[TestOpportunityStats] = Field(..., description="Test opportunity statistics")
    summary: TestOpportunitySummary = Field(..., description="Summary statistics")


class TestMonthlyTrend(BaseModel):
    """Schema for monthly test trends"""
    mes: int = Field(..., description="Month")
    codigo: str = Field(..., description="Test code")
    nombre: str = Field(..., description="Test name")
    total_casos: int = Field(..., description="Total cases")
    tiempo_promedio: float = Field(..., description="Average processing time")


class TestMonthlyTrendsResponse(BaseModel):
    """Response schema for monthly test trends"""
    trends: List[TestMonthlyTrend] = Field(..., description="Monthly trends")