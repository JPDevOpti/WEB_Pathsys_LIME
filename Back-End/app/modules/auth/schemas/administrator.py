from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdministratorCreate(BaseModel):
    name: str = Field(..., description="Administrator name")
    email: EmailStr = Field(..., description="Administrator email")
    password: str = Field(..., min_length=6, max_length=128, description="Administrator password")
    is_active: bool = Field(default=True, description="Whether the administrator is active")


class AdministratorResponse(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    role: str = "administrator"
    is_active: bool = True
    administrator_code: Optional[str] = None
