from pydantic import BaseModel, EmailStr
from typing import Optional


class UserInDB(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    role: str
    password_hash: str
    is_active: bool = True
    administrator_code: Optional[str] = None


class UserPublic(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    role: str
    is_active: bool = True
    administrator_code: Optional[str] = None


