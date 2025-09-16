from pydantic import Field
from app.shared.models.base import BaseDocument
from app.modules.patients.schemas.patient import Gender, CareType, EntityInfo

class Patient(BaseDocument):
    patient_code: str = Field(..., min_length=6, max_length=12)
    name: str = Field(..., min_length=2, max_length=200)
    age: int = Field(..., ge=0, le=150)
    gender: Gender = Field(...)
    entity_info: EntityInfo = Field(...)
    care_type: CareType = Field(...)
    observations: str = Field(None, max_length=500)
