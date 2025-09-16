from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    entity_code: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)

    @validator('name', pre=True)
    def validate_name(cls, v):
        if not v or not str(v).strip():
            raise ValueError('Entity name cannot be empty')
        return str(v).strip()

    @validator('entity_code', pre=True)
    def validate_entity_code(cls, v):
        if not v or not str(v).strip():
            raise ValueError('Entity code cannot be empty')
        return str(v).strip().upper()

class EntityCreate(EntityBase):
    pass

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    entity_code: Optional[str] = Field(None, min_length=1, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @validator('name', pre=True)
    def validate_name(cls, v):
        if v is not None:
            if not str(v).strip():
                raise ValueError('Entity name cannot be empty')
            return str(v).strip()
        return v

    @validator('entity_code', pre=True)
    def validate_entity_code(cls, v):
        if v is not None:
            if not str(v).strip():
                raise ValueError('Entity code cannot be empty')
            return str(v).strip().upper()
        return v

class EntityResponse(EntityBase):
    id: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EntitySearch(BaseModel):
    query: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
