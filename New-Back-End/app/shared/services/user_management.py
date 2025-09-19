from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr
from app.config.security import get_password_hash
from app.modules.auth.repositories.auth_repository import AuthRepository


class UserManagementService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.auth_repo = AuthRepository(db)

    async def check_email_exists_in_users(self, email: EmailStr) -> bool:
        """Check if a user with the given email already exists"""
        user = await self.auth_repo.get_user_by_email(email)
        return user is not None

    async def create_user_for_administrator(
        self,
        name: str,
        email: EmailStr,
        password: str,
        is_active: bool = True,
        administrator_code: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new administrator user"""
        try:
            # Check if user already exists
            if await self.check_email_exists_in_users(email):
                return None

            # Hash the password
            password_hash = get_password_hash(password)

            # Prepare user data
            user_data = {
                "name": name,
                "email": email,
                "role": "administrator",
                "password_hash": password_hash,
                "is_active": is_active,
                "administrator_code": administrator_code
            }

            # Insert user into database
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                # Return the created user data
                return {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email,
                    "role": "administrator",
                    "is_active": is_active,
                    "administrator_code": administrator_code
                }
            
            return None

        except Exception:
            return None
