from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class DiseaseBase(BaseModel):
    """Base model for disease"""
    table: str = Field(..., description="Reference table (e.g., CIE10)")
    code: str = Field(..., description="Disease code")
    name: str = Field(..., description="Disease name")
    description: Optional[str] = Field(None, description="General description of the disease")
    is_active: bool = Field(True, description="Active state of the disease")


class DiseaseCreate(DiseaseBase):
    """Model for creating a disease"""
    pass


class DiseaseResponse(DiseaseBase):
    """Model for disease response"""
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        populate_by_name = True
        from_attributes = True
