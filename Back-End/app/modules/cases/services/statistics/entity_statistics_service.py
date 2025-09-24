from typing import Dict, Any, Optional
from app.modules.cases.repositories.statistics.entity_statistics_repository import EntityStatisticsRepository


class EntityStatisticsService:
    """Service for entity statistics business logic"""
    
    def __init__(self, repository: EntityStatisticsRepository):
        self.repository = repository
    
    async def get_monthly_performance(
        self,
        month: int,
        year: int,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get monthly performance data for entities"""
        
        # Basic validation
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        return await self.repository.get_monthly_entity_performance(
            month=month,
            year=year,
            entity_name=entity_name
        )
    
    async def get_entity_details(
        self,
        entity_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get detailed statistics for a specific entity"""
        
        # Basic validation
        if not entity_name or not entity_name.strip():
            raise ValueError("Entity name is required")
        
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        return await self.repository.get_entity_details(
            entity_name=entity_name.strip(),
            month=month,
            year=year
        )
    
    async def get_entity_pathologists(
        self,
        entity_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Get pathologists who work with a specific entity"""
        
        # Basic validation
        if not entity_name or not entity_name.strip():
            raise ValueError("Entity name is required")
        
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        return await self.repository.get_entity_pathologists(
            entity_name=entity_name.strip(),
            month=month,
            year=year
        )
    
    async def debug_unique_entities(
        self,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Debug method to see all unique entities in cases"""
        
        # Basic validation
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        return await self.repository.debug_unique_entities(
            month=month,
            year=year
        )
    
    async def debug_all_entities_in_cases(
        self,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """Debug method to see ALL entities that have cases (any state)"""
        
        # Basic validation
        if not (1 <= month <= 12):
            raise ValueError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise ValueError("Year must be between 2020 and 2030")
        
        return await self.repository.debug_all_entities_in_cases(
            month=month,
            year=year
        )