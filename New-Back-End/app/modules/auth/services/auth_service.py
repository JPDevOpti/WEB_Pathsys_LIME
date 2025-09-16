from datetime import timedelta
from typing import Dict, Any
from pydantic import EmailStr
from app.config.database import get_database
from app.config.security import verify_password, create_access_token
from app.config.settings import settings
from app.modules.auth.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, repo: AuthRepository) -> None:
        self.repo = repo

    @classmethod
    async def build(cls) -> "AuthService":
        db = await get_database()
        return cls(AuthRepository(db))

    async def login(self, email: EmailStr, password: str) -> Dict[str, Any]:
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise ValueError("Credenciales inválidas")

        if not verify_password(password, user.get("password_hash", "")):
            raise ValueError("Credenciales inválidas")

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(subject=user["_id"], expires_delta=expires_delta)

        public_user = {
            "id": user.get("_id"),
            "nombre": user.get("nombre"),
            "email": user.get("email"),
            "rol": user.get("rol"),
            "is_active": user.get("is_active", True),
            "administrador_code": user.get("administrador_code"),
        }

        return {
            "token": {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": int(expires_delta.total_seconds()),
            },
            "user": public_user,
        }

    async def get_user_public_by_id(self, user_id: str) -> Dict[str, Any]:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado o inactivo")
        return {
            "id": user.get("_id"),
            "nombre": user.get("nombre"),
            "email": user.get("email"),
            "rol": user.get("rol"),
            "is_active": user.get("is_active", True),
            "administrador_code": user.get("administrador_code"),
        }


