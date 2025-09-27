from typing import Dict, Any
from app.core.exceptions import BadRequestError
from app.modules.cases.repositories.statistics.pathologist_statistics_repository import PathologistStatisticsRepository


class PathologistStatisticsService:
    """Service for pathologist statistics and analytics"""
    
    def __init__(self, repository: PathologistStatisticsRepository):
        self.repository = repository
    
    async def get_monthly_performance(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        pathologist_name: str = None
    ) -> Dict[str, Any]:
        """Get monthly performance data for pathologists"""
        
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        if threshold_days < 1 or threshold_days > 60:
            raise BadRequestError("Los días de oportunidad deben estar entre 1 y 60")
        
        try:
            return await self.repository.get_pathologist_monthly_performance(
                month, year, threshold_days, pathologist_name
            )
        except Exception as e:
            raise BadRequestError(f"Error obteniendo rendimiento de patólogos: {str(e)}")
    
    async def get_pathologist_entities(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get entities where a pathologist works"""
        
        if not pathologist_name or len(pathologist_name.strip()) == 0:
            raise BadRequestError("El nombre del patólogo es requerido")
        
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        try:
            return await self.repository.get_pathologist_entities(
                pathologist_name.strip(), month, year
            )
        except Exception as e:
            raise BadRequestError(f"Error obteniendo entidades del patólogo: {str(e)}")
    
    async def get_pathologist_tests(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get tests performed by a pathologist"""
        
        if not pathologist_name or len(pathologist_name.strip()) == 0:
            raise BadRequestError("El nombre del patólogo es requerido")
        
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        try:
            return await self.repository.get_pathologist_tests(
                pathologist_name.strip(), month, year
            )
        except Exception as e:
            raise BadRequestError(f"Error obteniendo pruebas del patólogo: {str(e)}")
    
    async def get_pathologist_opportunity_summary(
        self,
        pathologist_name: str,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        """Get opportunity summary for a specific pathologist"""
        
        if not pathologist_name or len(pathologist_name.strip()) == 0:
            raise BadRequestError("El nombre del patólogo es requerido")
        
        if threshold_days < 1 or threshold_days > 60:
            raise BadRequestError("Los días de oportunidad deben estar entre 1 y 60")
        
        try:
            return await self.repository.get_pathologist_opportunity_summary(
                pathologist_name.strip(), threshold_days
            )
        except Exception as e:
            raise BadRequestError(f"Error obteniendo resumen de oportunidad: {str(e)}")
    
    async def get_pathologist_monthly_trends(
        self,
        pathologist_name: str,
        year: int,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        """Get monthly trends for a pathologist throughout the year"""
        
        if not pathologist_name or len(pathologist_name.strip()) == 0:
            raise BadRequestError("El nombre del patólogo es requerido")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        if threshold_days < 1 or threshold_days > 60:
            raise BadRequestError("Los días de oportunidad deben estar entre 1 y 60")
        
        try:
            return await self.repository.get_pathologist_monthly_trends(
                pathologist_name.strip(), year, threshold_days
            )
        except Exception as e:
            raise BadRequestError(f"Error obteniendo tendencias mensuales: {str(e)}")