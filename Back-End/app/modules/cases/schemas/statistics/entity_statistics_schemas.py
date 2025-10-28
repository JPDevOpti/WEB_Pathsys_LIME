from typing import List, Optional
from pydantic import BaseModel, Field


class EntityStats(BaseModel):
    """Estadísticas por entidad en el mes"""
    nombre: str = Field(..., description="Nombre de la entidad")
    codigo: str = Field(..., description="Código de la entidad")
    ambulatorios: int = Field(..., description="Total de casos ambulatorios")
    hospitalizados: int = Field(..., description="Total de casos hospitalizados")
    total: int = Field(..., description="Total de casos completados")
    avg_business_days: float = Field(..., description="Promedio de días hábiles")

    class Config:
        from_attributes = True


class EntitySummary(BaseModel):
    """Resumen de rendimiento mensual por entidades"""
    total: int = Field(..., description="Total de casos completados")
    ambulatorios: int = Field(..., description="Total de casos ambulatorios")
    hospitalizados: int = Field(..., description="Total de casos hospitalizados")
    tiempoPromedio: float = Field(..., description="Tiempo promedio de procesamiento en días")

    class Config:
        from_attributes = True


class MonthlyEntityPerformanceResponse(BaseModel):
    """Respuesta de rendimiento mensual por entidades"""
    entities: List[EntityStats] = Field(..., description="Listado de entidades con estadísticas")
    summary: EntitySummary = Field(..., description="Resumen de estadísticas")

    class Config:
        from_attributes = True


class BasicStats(BaseModel):
    """Estadísticas básicas de la entidad"""
    total_pacientes: int = Field(..., description="Total de pacientes")
    ambulatorios: int = Field(..., description="Total de pacientes ambulatorios")
    hospitalizados: int = Field(..., description="Total de pacientes hospitalizados")
    promedio_muestras_por_paciente: float = Field(..., description="Promedio de muestras por paciente")


class ProcessingTimes(BaseModel):
    """Tiempos de procesamiento (días hábiles)"""
    minimo_dias: float = Field(..., description="Mínimo de días hábiles")
    maximo_dias: float = Field(..., description="Máximo de días hábiles")
    promedio_dias: float = Field(..., description="Promedio de días hábiles")
    muestras_completadas: int = Field(..., description="Total de casos completados")


class TopRequestedTest(BaseModel):
    """Prueba más solicitada en la entidad"""
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    total_solicitudes: int = Field(..., description="Total de solicitudes")


class EntityDetails(BaseModel):
    """Bloque de detalles estadísticos de la entidad"""
    estadisticas_basicas: BasicStats = Field(..., description="Estadísticas básicas")
    tiempos_procesamiento: ProcessingTimes = Field(..., description="Tiempos de procesamiento")
    pruebas_mas_solicitadas: List[TopRequestedTest] = Field(..., description="Pruebas más solicitadas")


class EntityDetailsResponse(BaseModel):
    """Respuesta de detalles de una entidad"""
    detalles: EntityDetails = Field(..., description="Detalles estadísticos")

    class Config:
        from_attributes = True


class PathologistEntityStats(BaseModel):
    """Estadísticas de patólogos asociados a una entidad"""
    codigo: str = Field(..., description="Código del patólogo")
    nombre: str = Field(..., description="Nombre del patólogo")
    total_casos: int = Field(..., description="Total de casos del patólogo")
    casos_completados: int = Field(..., description="Casos completados por el patólogo")
    tiempo_promedio: float = Field(..., description="Promedio de días hábiles")


class EntityPathologistsResponse(BaseModel):
    """Respuesta de patólogos por entidad"""
    patologos: List[PathologistEntityStats] = Field(..., description="Listado de patólogos")

    class Config:
        from_attributes = True
