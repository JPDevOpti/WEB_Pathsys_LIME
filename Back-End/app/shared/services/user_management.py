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

    async def create_user_for_pathologist(
        self,
        name: str,
        email: EmailStr,
        password: str,
        pathologist_code: str,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new pathologist user"""
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
                "role": "pathologist",
                "password_hash": password_hash,
                "is_active": is_active,
                "pathologist_code": pathologist_code
            }

            # Insert user into database
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                # Return the created user data
                return {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email,
                    "role": "pathologist",
                    "is_active": is_active,
                    "pathologist_code": pathologist_code
                }
            
            return None

        except Exception:
            return None

    async def create_user_for_auxiliar(
        self,
        name: str,
        email: EmailStr,
        password: str,
        auxiliar_code: str,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new auxiliar user"""
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
                "role": "auxiliar",
                "password_hash": password_hash,
                "is_active": is_active,
                "auxiliar_code": auxiliar_code
            }

            # Insert user into database
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                # Return the created user data
                return {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email,
                    "role": "auxiliar",
                    "is_active": is_active,
                    "auxiliar_code": auxiliar_code
                }
            
            return None

        except Exception:
            return None

    async def create_user_for_billing(
        self,
        name: str,
        email: EmailStr,
        password: str,
        billing_code: str,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new billing user"""
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
                "role": "billing",
                "password_hash": password_hash,
                "is_active": is_active,
                "billing_code": billing_code
            }

            # Insert user into database
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                # Return the created user data
                return {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email,
                    "role": "billing",
                    "is_active": is_active,
                    "billing_code": billing_code
                }
            
            return None

        except Exception:
            return None

    async def create_user_for_resident(
        self,
        name: str,
        email: EmailStr,
        password: str,
        resident_code: str,
        is_active: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Create a new resident user"""
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
                "role": "resident",
                "password_hash": password_hash,
                "is_active": is_active,
                "resident_code": resident_code
            }

            # Insert user into database
            result = await self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                # Return the created user data
                return {
                    "id": str(result.inserted_id),
                    "name": name,
                    "email": email,
                    "role": "resident",
                    "is_active": is_active,
                    "resident_code": resident_code
                }
            
            return None

        except Exception:
            return None

    async def update_user_for_auxiliar(
        self,
        auxiliar_code: str,
        name: Optional[str] = None,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an auxiliar user"""
        try:
            user = await self.db.users.find_one({"auxiliar_code": auxiliar_code})
            if not user:
                return None

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                existing_user = await self.db.users.find_one({"email": email, "_id": {"$ne": user["_id"]}})
                if existing_user:
                    return None
                update_data["email"] = email
            if password is not None:
                update_data["password_hash"] = get_password_hash(password)
            if is_active is not None:
                update_data["is_active"] = is_active

            if not update_data:
                return user

            result = await self.db.users.update_one(
                {"auxiliar_code": auxiliar_code},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_user = await self.db.users.find_one({"auxiliar_code": auxiliar_code})
                return {
                    "id": str(updated_user["_id"]),
                    "name": updated_user["name"],
                    "email": updated_user["email"],
                    "role": updated_user["role"],
                    "is_active": updated_user["is_active"],
                    "auxiliar_code": updated_user["auxiliar_code"]
                }
            
            return None
        except Exception:
            return None

    async def update_user_for_billing(
        self,
        billing_code: str,
        name: Optional[str] = None,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a billing user"""
        try:
            user = await self.db.users.find_one({"billing_code": billing_code})
            if not user:
                return None

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                existing_user = await self.db.users.find_one({"email": email, "_id": {"$ne": user["_id"]}})
                if existing_user:
                    return None
                update_data["email"] = email
            if password is not None:
                update_data["password_hash"] = get_password_hash(password)
            if is_active is not None:
                update_data["is_active"] = is_active

            if not update_data:
                return user

            result = await self.db.users.update_one(
                {"billing_code": billing_code},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_user = await self.db.users.find_one({"billing_code": billing_code})
                return {
                    "id": str(updated_user["_id"]),
                    "name": updated_user["name"],
                    "email": updated_user["email"],
                    "role": updated_user["role"],
                    "is_active": updated_user["is_active"],
                    "billing_code": updated_user["billing_code"]
                }
            
            return None
        except Exception:
            return None

    async def update_user_for_pathologist(
        self,
        pathologist_code: str,
        name: Optional[str] = None,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a pathologist user"""
        try:
            user = await self.db.users.find_one({"pathologist_code": pathologist_code})
            if not user:
                return None

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                existing_user = await self.db.users.find_one({"email": email, "_id": {"$ne": user["_id"]}})
                if existing_user:
                    return None
                update_data["email"] = email
            if password is not None:
                update_data["password_hash"] = get_password_hash(password)
            if is_active is not None:
                update_data["is_active"] = is_active

            if not update_data:
                return user

            result = await self.db.users.update_one(
                {"pathologist_code": pathologist_code},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_user = await self.db.users.find_one({"pathologist_code": pathologist_code})
                return {
                    "id": str(updated_user["_id"]),
                    "name": updated_user["name"],
                    "email": updated_user["email"],
                    "role": updated_user["role"],
                    "is_active": updated_user["is_active"],
                    "pathologist_code": updated_user["pathologist_code"]
                }
            
            return None
        except Exception:
            return None

    async def update_user_for_resident(
        self,
        resident_code: str,
        name: Optional[str] = None,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a resident user"""
        try:
            user = await self.db.users.find_one({"resident_code": resident_code})
            if not user:
                return None

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if email is not None:
                existing_user = await self.db.users.find_one({"email": email, "_id": {"$ne": user["_id"]}})
                if existing_user:
                    return None
                update_data["email"] = email
            if password is not None:
                update_data["password_hash"] = get_password_hash(password)
            if is_active is not None:
                update_data["is_active"] = is_active

            if not update_data:
                return user

            result = await self.db.users.update_one(
                {"resident_code": resident_code},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                updated_user = await self.db.users.find_one({"resident_code": resident_code})
                return {
                    "id": str(updated_user["_id"]),
                    "name": updated_user["name"],
                    "email": updated_user["email"],
                    "role": updated_user["role"],
                    "is_active": updated_user["is_active"],
                    "resident_code": updated_user["resident_code"]
                }
            
            return None
        except Exception:
            return None
