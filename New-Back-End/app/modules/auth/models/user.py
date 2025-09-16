from pydantic import BaseModel, EmailStr
from typing import Optional


class UserInDB(BaseModel):
    id: Optional[str] = None
    nombre: str
    email: EmailStr
    rol: str
    password_hash: str
    is_active: bool = True
    administrador_code: Optional[str] = None


class UserPublic(BaseModel):
    id: Optional[str] = None
    nombre: str
    email: EmailStr
    rol: str
    is_active: bool = True
    administrador_code: Optional[str] = None


