from typing import List, Optional, Dict, Any
from fastapi import HTTPException
import logging

from app.modules.diseases.repositories.disease_repository import DiseaseRepository
from app.modules.diseases.models.disease import DiseaseCreate, DiseaseResponse

logger = logging.getLogger(__name__)


class DiseaseService:
    """Service for disease operations"""
    
    def __init__(self, repository: DiseaseRepository):
        self.repository = repository
    
    async def create_disease(self, disease: DiseaseCreate) -> DiseaseResponse:
        """Create a new disease"""
        try:
            # Check if a disease with the same code already exists
            existing = await self.repository.get_by_code(disease.code)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"A disease with code {disease.code} already exists"
                )
            
            # Create the disease
            created_disease = await self.repository.create(disease)
            
            return created_disease
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating disease: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def get_disease_by_code(self, code: str) -> Optional[DiseaseResponse]:
        """Get disease by code"""
        try:
            disease = await self.repository.get_by_code(code)
            return disease
        except Exception as e:
            logger.error(f"Error getting disease by code {code}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_all_diseases(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get all diseases"""
        try:
            # If not specified, filter only active by default
            if is_active is None:
                is_active = True
                
            diseases = await self.repository.get_all(skip, limit, is_active)
            total = await self.repository.count_total(is_active)
            
            return {
                "diseases": diseases,
                "total": total,
                "skip": skip,
                "limit": limit,
                "has_next": skip + len(diseases) < total,
                "has_prev": skip > 0
            }
        except Exception as e:
            logger.error(f"Error getting diseases: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def search_diseases_by_name(
        self, 
        name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search diseases by name"""
        try:
            diseases = await self.repository.search_by_name(name, skip, limit)
            
            return {
                "diseases": diseases,
                "search_term": name,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error searching diseases by name: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def search_diseases_by_code(
        self, 
        code: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Search diseases by code"""
        try:
            diseases = await self.repository.search_by_code(code, skip, limit)
            
            return {
                "diseases": diseases,
                "search_term": code,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error searching diseases by code: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_diseases_by_table(
        self, 
        table: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get diseases by reference table"""
        try:
            diseases = await self.repository.get_by_table(table, skip, limit)
            
            return {
                "diseases": diseases,
                "table": table,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error getting diseases from table {table}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_disease(self, disease_id: str) -> bool:
        """Delete a disease"""
        try:
            # Delete the disease
            success = await self.repository.delete(disease_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Disease not found")
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting disease {disease_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
