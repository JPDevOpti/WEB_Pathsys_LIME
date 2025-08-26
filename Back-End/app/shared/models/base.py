from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId

class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId format")
        raise ValueError("ObjectId required")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, handler):
        field_schema.update(type="string", format="objectid")
        return field_schema

class BaseDocument(BaseModel):
    """Modelo base para documentos de MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    fecha_creacion: Optional[datetime] = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)
    isActive: bool = Field(default=True)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True

class BaseCreateModel(BaseModel):
    """Modelo base para creación de documentos"""
    pass

class BaseUpdateModel(BaseModel):
    """Modelo base para actualización de documentos"""
    fecha_actualizacion: Optional[datetime] = Field(default_factory=datetime.utcnow)

class BaseResponseModel(BaseModel):
    """Modelo base para respuestas de API"""
    id: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    isActive: bool
    
    class Config:
        from_attributes = True

class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp"""
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

class SoftDeleteMixin(BaseModel):
    """Mixin para soft delete"""
    isActive: bool = Field(default=True)
    fecha_eliminacion: Optional[datetime] = None
    eliminado_por: Optional[str] = None