from typing import Dict, Any, Optional, List
from app.modules.cases.repositories.statistics.test_statistics_repository import TestStatisticsRepository
from app.core.exceptions import BadRequestError


class TestStatisticsService:
    """Service for test statistics business logic"""
    
    def __init__(self, repository: TestStatisticsRepository):
        self.repository = repository
    
    async def get_monthly_test_performance(
        self, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get monthly performance statistics for all tests"""
        
        # Validate inputs
        if not (1 <= month <= 12):
            raise BadRequestError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        return await self.repository.get_monthly_test_performance(month, year, entity_name)
    
    async def get_test_details(
        self, 
        test_code: str, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed statistics for a specific test"""
        
        # Validate inputs
        if not test_code or not test_code.strip():
            raise BadRequestError("Test code is required")
        
        if not (1 <= month <= 12):
            raise BadRequestError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        return await self.repository.get_test_details(test_code.strip(), month, year, entity_name)
    
    async def get_test_pathologists(
        self, 
        test_code: str, 
        month: int, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pathologists who worked on a specific test"""
        
        # Validate inputs
        if not test_code or not test_code.strip():
            raise BadRequestError("Test code is required")
        
        if not (1 <= month <= 12):
            raise BadRequestError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        return await self.repository.get_test_pathologists(test_code.strip(), month, year, entity_name)
    
    async def get_test_opportunity_summary(
        self, 
        month: int, 
        year: int, 
        threshold_days: int = 7,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get opportunity summary for tests"""
        
        # Validate inputs
        if not (1 <= month <= 12):
            raise BadRequestError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        if not (1 <= threshold_days <= 60):
            raise BadRequestError("Threshold days must be between 1 and 60")
        
        return await self.repository.get_test_opportunity_summary(month, year, threshold_days, entity_name)
    
    async def debug_cases_structure(
        self, 
        month: int, 
        year: int
    ) -> Dict[str, Any]:
        """Debug method to see the actual structure of cases"""
        
        # Validate inputs
        if not (1 <= month <= 12):
            raise BadRequestError("Month must be between 1 and 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        return await self.repository.debug_cases_structure(month, year)
    
    async def get_test_monthly_trends(
        self, 
        year: int, 
        entity_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get monthly trends for tests"""
        
        # Validate inputs
        if year < 2020 or year > 2030:
            raise BadRequestError("Year must be between 2020 and 2030")
        
        return await self.repository.get_test_monthly_trends(year, entity_name)