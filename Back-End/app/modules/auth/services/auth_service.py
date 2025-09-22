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
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.get("password_hash", "")):
            raise ValueError("Invalid credentials")

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(subject=user["_id"], expires_delta=expires_delta)

        public_user = {
            "id": user.get("_id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "is_active": user.get("is_active", True),
            "administrator_code": user.get("administrator_code"),
            "pathologist_code": user.get("pathologist_code"),
            "resident_code": user.get("resident_code"),
            "auxiliary_code": user.get("auxiliary_code"),
            "billing_code": user.get("billing_code"),
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
            raise ValueError("User not found or inactive")
        return {
            "id": user.get("_id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role"),
            "is_active": user.get("is_active", True),
            "administrator_code": user.get("administrator_code"),
            "pathologist_code": user.get("pathologist_code"),
            "resident_code": user.get("resident_code"),
            "auxiliary_code": user.get("auxiliary_code"),
            "billing_code": user.get("billing_code"),
        }


