from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class TestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    test_code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    time: int = Field(default=6, gt=0, le=1440)
    price: float = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

    @validator('name', pre=True)
    def validate_name(cls, v):
        if not v or not str(v).strip():
            raise ValueError('Test name cannot be empty')
        return str(v).strip()

    @validator('test_code', pre=True)
    def validate_test_code(cls, v):
        if not v or not str(v).strip():
            raise ValueError('Test code cannot be empty')
        return str(v).strip().upper()

class TestCreate(TestBase):
    pass

class TestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    test_code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    time: Optional[int] = Field(None, gt=0, le=1440)
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @validator('name', pre=True)
    def validate_name(cls, v):
        if v is not None:
            if not str(v).strip():
                raise ValueError('Test name cannot be empty')
            return str(v).strip()
        return v

    @validator('test_code', pre=True)
    def validate_test_code(cls, v):
        if v is not None:
            if not str(v).strip():
                raise ValueError('Test code cannot be empty')
            return str(v).strip().upper()
        return v

class TestResponse(TestBase):
    id: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TestSearch(BaseModel):
    query: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
