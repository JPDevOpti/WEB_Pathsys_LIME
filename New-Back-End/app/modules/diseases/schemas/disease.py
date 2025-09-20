from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DiseaseCreateSchema(BaseModel):
    """Schema for creating a disease"""
    table: str = Field(..., description="Reference table (e.g., CIE10)")
    code: str = Field(..., description="Disease code")
    name: str = Field(..., description="Disease name")
    description: Optional[str] = Field(None, description="General description of the disease")
    is_active: bool = Field(True, description="Active state of the disease")


class DiseaseResponseSchema(BaseModel):
    """Schema for disease response"""
    id: str = Field(..., description="Disease ID")
    table: str = Field(..., description="Reference table")
    code: str = Field(..., description="Disease code")
    name: str = Field(..., description="Disease name")
    description: Optional[str] = Field(None, description="General description of the disease")
    is_active: bool = Field(..., description="Active state of the disease")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: datetime = Field(..., description="Last update date")


class DiseaseListResponseSchema(BaseModel):
    """Schema for disease list response"""
    diseases: List[DiseaseResponseSchema] = Field(..., description="List of diseases")
    total: int = Field(..., description="Total number of diseases")
    skip: int = Field(..., description="Number of elements skipped")
    limit: int = Field(..., description="Limit of elements per page")


class DiseaseSearchResponseSchema(BaseModel):
    """Schema for disease search response"""
    diseases: List[DiseaseResponseSchema] = Field(..., description="List of found diseases")
    search_term: str = Field(..., description="Search term used")
    skip: int = Field(..., description="Number of elements skipped")
    limit: int = Field(..., description="Limit of elements per page")


class DiseaseByTableResponseSchema(BaseModel):
    """Schema for diseases by table response"""
    diseases: List[DiseaseResponseSchema] = Field(..., description="List of diseases from the table")
    table: str = Field(..., description="Reference table")
    skip: int = Field(..., description="Number of elements skipped")
    limit: int = Field(..., description="Limit of elements per page")
