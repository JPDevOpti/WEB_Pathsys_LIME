from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class EntityInfo(BaseModel):
    id: str = Field(..., min_length=1, max_length=50, description="ID de la entidad")
    name: str = Field(..., min_length=2, max_length=100, description="Nombre de la entidad")


class Gender(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class CareType(str, Enum):
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"

class IdentificationType(int, Enum):
    CEDULA_CIUDADANIA = 1
    CEDULA_EXTRANJERIA = 2
    TARJETA_IDENTIDAD = 3
    PASAPORTE = 4
    REGISTRO_CIVIL = 5
    DOCUMENTO_EXTRANJERO = 6
    NIT = 7
    CARNET_DIPLOMATICO = 8
    SALVOCONDUCTO = 9

class Location(BaseModel):
    municipality_code: str = Field(..., min_length=1, max_length=10, description="Código del municipio")
    municipality_name: str = Field(..., min_length=2, max_length=100, description="Nombre del municipio")
    subregion: str = Field(..., min_length=2, max_length=100, description="Subregión")
    address: str = Field(..., min_length=5, max_length=200, description="Dirección de residencia")

    class Config:
        populate_by_name = True

class PatientBase(BaseModel):
    patient_code: str = Field(..., description="Código único del paciente")
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

    @validator('identification_number', pre=True)
    def validate_identification_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Identification number cannot be empty')
        # Remove any non-digit characters
        clean_number = ''.join(c for c in str(v) if c.isdigit())
        if not clean_number:
            raise ValueError('Identification number must contain at least one digit')
        if len(clean_number) < 5 or len(clean_number) > 12:
            raise ValueError('Identification number must be between 5 and 12 digits')
        return clean_number

    @validator('first_name', 'second_name', 'first_lastname', 'second_lastname', pre=True)
    def validate_name_fields(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name field cannot be empty')
            # Validate that name contains only letters, spaces, and common name characters
            clean_name = v.strip()
            if not all(c.isalpha() or c.isspace() or c in "'-." for c in clean_name):
                raise ValueError('Name field can only contain letters, spaces, apostrophes, hyphens, and periods')
            return clean_name.title()
        return v

    @validator('birth_date', pre=True)
    def validate_birth_date(cls, v):
        if isinstance(v, str):
            try:
                birth_date = datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Birth date must be in YYYY-MM-DD format')
        else:
            birth_date = v
        
        # Validate that birth date is not in the future
        if birth_date > date.today():
            raise ValueError('Birth date cannot be in the future')
        
        # Validate reasonable age limits (0-150 years)
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age > 150:
            raise ValueError('Age cannot exceed 150 years')
        
        return birth_date



    class Config:
        populate_by_name = True
        use_enum_values = True

class PatientCreate(PatientBase):
    patient_code: Optional[str] = Field(None, description="Código único del paciente (se genera automáticamente si no se proporciona)")

class PatientUpdate(BaseModel):
    patient_code: Optional[str] = Field(None, description="Código único del paciente")
    identification_type: Optional[IdentificationType] = None
    identification_number: Optional[str] = Field(None, min_length=5, max_length=12)
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    second_name: Optional[str] = Field(None, min_length=2, max_length=50)
    first_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    second_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    location: Optional[Location] = None
    entity_info: Optional[EntityInfo] = None
    care_type: Optional[CareType] = None
    observations: Optional[str] = Field(None, max_length=500)

    @validator('identification_number', pre=True)
    def validate_identification_number(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Identification number cannot be empty')
            clean_number = ''.join(c for c in str(v) if c.isdigit())
            if not clean_number:
                raise ValueError('Identification number must contain at least one digit')
            if len(clean_number) < 5 or len(clean_number) > 12:
                raise ValueError('Identification number must be between 5 and 12 digits')
            return clean_number
        return v

    @validator('first_name', 'second_name', 'first_lastname', 'second_lastname', pre=True)
    def validate_name_fields(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name field cannot be empty')
            clean_name = v.strip()
            if not all(c.isalpha() or c.isspace() or c in "'-." for c in clean_name):
                raise ValueError('Name field can only contain letters, spaces, apostrophes, hyphens, and periods')
            return clean_name.title()
        return v

    @validator('birth_date', pre=True)
    def validate_birth_date(cls, v):
        if v is not None:
            if isinstance(v, str):
                try:
                    birth_date = datetime.strptime(v, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Birth date must be in YYYY-MM-DD format')
            else:
                birth_date = v
            
            if birth_date > date.today():
                raise ValueError('Birth date cannot be in the future')
            
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age > 150:
                raise ValueError('Age cannot exceed 150 years')
            
            return birth_date
        return v

    class Config:
        use_enum_values = True

class PatientResponse(PatientBase):
    id: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class PatientSearch(BaseModel):
    identification_type: Optional[IdentificationType] = None
    identification_number: Optional[str] = Field(None, min_length=1, max_length=12)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    first_lastname: Optional[str] = Field(None, min_length=1, max_length=50)
    birth_date_from: Optional[date] = None
    birth_date_to: Optional[date] = None
    age_min: Optional[int] = Field(None, ge=0, le=150)
    age_max: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Gender] = None
    municipality_code: Optional[str] = Field(None, min_length=1, max_length=10)
    municipality_name: Optional[str] = Field(None, min_length=1, max_length=100)
    subregion: Optional[str] = Field(None, min_length=1, max_length=100)
    entity: Optional[str] = Field(None, min_length=1, max_length=100)
    care_type: Optional[CareType] = None
    date_from: Optional[str] = Field(None, description="Fecha desde en formato YYYY-MM-DD")
    date_to: Optional[str] = Field(None, description="Fecha hasta en formato YYYY-MM-DD")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    @validator('age_min', 'age_max')
    def validate_age_range(cls, v, values):
        if 'age_min' in values and 'age_max' in values:
            age_min = values.get('age_min')
            age_max = v if v is not None else values.get('age_max')
            if age_min is not None and age_max is not None and age_min > age_max:
                raise ValueError('age_min cannot be greater than age_max')
        return v

    @validator('birth_date_from', 'birth_date_to', pre=True)
    def validate_search_dates(cls, v):
        if v is not None:
            if isinstance(v, str):
                try:
                    return datetime.strptime(v, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @validator('date_from', 'date_to', pre=True)
    def validate_date_strings(cls, v):
        if v is not None and v.strip():
            try:
                datetime.strptime(v.strip(), '%Y-%m-%d')
                return v.strip()
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return None

    class Config:
        use_enum_values = True
