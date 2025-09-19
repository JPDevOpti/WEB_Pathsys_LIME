from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

class EntityInfo(BaseModel):
    id: str = Field(...)
    name: str = Field(...)

class Gender(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class CareType(str, Enum):
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"

class PatientBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    age: int = Field(..., ge=0, le=150)
    gender: Gender = Field(...)
    entity_info: EntityInfo = Field(...)
    care_type: CareType = Field(...)
    observations: Optional[str] = Field(None, max_length=500)

    @validator('name', pre=True)
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Patient name cannot be empty')
        return ' '.join(word.capitalize() for word in v.strip().split())

    class Config:
        populate_by_name = True
        use_enum_values = True

class PatientCreate(PatientBase):
    patient_code: str = Field(...)
    
    @validator('patient_code', pre=True)
    def validate_patient_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Patient code cannot be empty')
        code_clean = ''.join(c for c in v if c.isdigit())
        if not code_clean:
            raise ValueError('Patient code must contain at least one digit')
        if len(code_clean) < 6 or len(code_clean) > 12:
            raise ValueError('Patient code must be between 6 and 12 digits')
        return code_clean

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Gender] = None
    entity_info: Optional[EntityInfo] = None
    care_type: Optional[CareType] = None
    observations: Optional[str] = Field(None, max_length=500)

    @validator('name', pre=True)
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Patient name cannot be empty')
            return ' '.join(word.capitalize() for word in v.strip().split())
        return v

    class Config:
        use_enum_values = True

class PatientResponse(PatientBase):
    id: str = Field(...)
    patient_code: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class PatientSearch(BaseModel):
    name: Optional[str] = None
    patient_code: Optional[str] = None
    age_min: Optional[int] = Field(None, ge=0)
    age_max: Optional[int] = Field(None, le=150)
    entity: Optional[str] = None
    gender: Optional[Gender] = None
    care_type: Optional[CareType] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    class Config:
        use_enum_values = True
