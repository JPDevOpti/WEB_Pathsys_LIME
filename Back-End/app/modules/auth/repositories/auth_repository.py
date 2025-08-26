"""Repositorio de autenticación"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.auth.models.auth import AuthUser
from app.core.exceptions import NotFoundError
from app.config.security import verify_password as verify_pwd
from bson import ObjectId


class AuthRepository:
    """Repositorio para operaciones de autenticación"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.usuarios
    
    async def get_user_by_email(self, email: str) -> Optional[AuthUser]:
        """Obtener usuario por email"""
        # Buscar usuario activo (puede tener campo 'activo' o 'is_active')
        user_doc = await self.collection.find_one({
            "email": email,
            "$or": [
                {"activo": True},
                {"is_active": True},
                {"activo": {"$exists": False}, "is_active": {"$exists": False}}  # Si no tiene campo de activo, considerar activo
            ]
        })
        if not user_doc:
            return None
        
        # Convertir ObjectId a string
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        
        # Normalizar campos para compatibilidad
        if "is_active" in user_doc and "activo" not in user_doc:
            user_doc["activo"] = user_doc["is_active"]
        
        # Asegurar que tenga username
        if "username" not in user_doc or not user_doc["username"]:
            user_doc["username"] = user_doc.get("nombre", user_doc["email"])
        
        # Manejar nombres y apellidos desde el campo 'nombre'
        if "nombre" in user_doc and not user_doc.get("nombres"):
            nombre_completo = user_doc["nombre"].split()
            if len(nombre_completo) >= 2:
                user_doc["nombres"] = " ".join(nombre_completo[:-1])
                user_doc["apellidos"] = nombre_completo[-1]
            else:
                user_doc["nombres"] = user_doc["nombre"]
                user_doc["apellidos"] = ""
        
        # Asegurar que tenga rol como lista para compatibilidad
        if "rol" in user_doc and "roles" not in user_doc:
            user_doc["roles"] = [user_doc["rol"]]
        
        return AuthUser(**user_doc)
    
    async def get_user_by_username(self, username: str) -> Optional[AuthUser]:
        """Obtener usuario por nombre de usuario"""
        user_doc = await self.collection.find_one({"username": username, "activo": True})
        if not user_doc:
            return None
        
        # Convertir ObjectId a string
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        
        return AuthUser(**user_doc)
    
    async def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Obtener usuario por ID"""
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id), "activo": True})
            if not user_doc:
                return None
            
            # Convertir ObjectId a string
            user_doc["id"] = str(user_doc["_id"])
            del user_doc["_id"]
            
            return AuthUser(**user_doc)
        except Exception:
            return None
    
    async def verify_password(self, email: str, password: str) -> bool:
        """Verificar contraseña del usuario"""
        # Buscar usuario activo (puede tener campo 'activo' o 'is_active')
        user_doc = await self.collection.find_one({
            "email": email,
            "$or": [
                {"activo": True},
                {"is_active": True},
                {"activo": {"$exists": False}, "is_active": {"$exists": False}}  # Si no tiene campo de activo, considerar activo
            ]
        })
        if not user_doc:
            return False
        
        # Verificar si tiene password_hash (hasheado) o password (simple)
        stored_password = user_doc.get("password_hash") or user_doc.get("password")
        
        if not stored_password:
            return False
        
        # Si tiene password_hash, verificar con bcrypt
        if user_doc.get("password_hash"):
            try:
                return verify_pwd(password, stored_password)
            except Exception as e:
                print(f"Error verificando password: {e}")
                return False
        else:
            # Comparación simple para passwords no hasheados
            return stored_password == password
    
    async def update_last_login(self, user_id: str) -> bool:
        """Actualizar último acceso del usuario"""
        from datetime import datetime
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"ultimo_acceso": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False