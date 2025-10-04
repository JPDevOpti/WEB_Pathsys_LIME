from datetime import date
from typing import Optional
from pydantic import Field
from app.shared.models.base import BaseDocument
from app.modules.patients.schemas.patient import (
    Gender, CareType, EntityInfo, IdentificationType, Location
)

class Patient(BaseDocument):
    identification_type: IdentificationType = Field(...)
    identification_number: str = Field(..., min_length=5, max_length=12)
    first_name: str = Field(..., min_length=2, max_length=50)
    second_name: Optional[str] = Field(None, min_length=2, max_length=50)
    first_lastname: str = Field(..., min_length=2, max_length=50)
    second_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: date = Field(...)
    gender: Gender = Field(...)
    location: Location = Field(...)
    entity_info: EntityInfo = Field(...)
    care_type: CareType = Field(...)
    observations: Optional[str] = Field(None, max_length=500)
