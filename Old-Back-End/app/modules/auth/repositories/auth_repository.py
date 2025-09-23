"""Repositorio de autenticación"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.auth.models.auth import AuthUser
from app.core.exceptions import NotFoundError
from app.config.security import verify_password as verify_pwd
from bson import ObjectId
from datetime import datetime, timezone
import logging

# Configurar logger
logger = logging.getLogger(__name__)
class AuthRepository:
    """Repositorio para operaciones de autenticación"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.usuarios
    
    async def get_user_by_email(self, email: str) -> Optional[AuthUser]:
        """Obtener usuario por email"""
        # Buscar usuario activo usando el campo real de la BD
        user_doc = await self.collection.find_one({
            "email": email,
            "is_active": True
        })
        if not user_doc:
            return None
        
        # Convertir ObjectId a string
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        
        return AuthUser(**user_doc)
    
    async def get_user_by_username(self, username: str) -> Optional[AuthUser]:
        """Obtener usuario por nombre de usuario (usando nombre completo)"""
        user_doc = await self.collection.find_one({
            "nombre": username,
            "is_active": True
        })
        if not user_doc:
            return None
        
        # Convertir ObjectId a string
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        
        return AuthUser(**user_doc)
    
    async def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Obtener usuario por ID"""
        try:
            # Validar formato de ObjectId
            if not ObjectId.is_valid(user_id):
                logger.warning(f"ID de usuario inválido: {user_id}")
                return None
            
            user_doc = await self.collection.find_one({
                "_id": ObjectId(user_id),
                "is_active": True
            })
            if not user_doc:
                return None
            
            # Convertir ObjectId a string
            user_doc["id"] = str(user_doc["_id"])
            del user_doc["_id"]
            
            return AuthUser(**user_doc)
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID {user_id}: {str(e)}")
            return None
    
    async def verify_password(self, email: str, password: str) -> bool:
        """Verificar contraseña del usuario"""
        # Buscar usuario activo usando el campo real de la BD
        user_doc = await self.collection.find_one({
            "email": email,
            "is_active": True
        })
        if not user_doc:
            return False
        
        # Verificar si tiene password_hash (hasheado)
        stored_password_hash = user_doc.get("password_hash")
        
        if not stored_password_hash:
            # Si no tiene password_hash, no permitir autenticación
            logger.warning(f"Usuario {email} no tiene contraseña hasheada")
            return False
        # Verificar con bcrypt
        try:
            return verify_pwd(password, stored_password_hash)
        except Exception as e:
            # Log del error pero no exponer detalles
            logger.error(f"Error verificando password hash para {email}: {str(e)}")
            return False
    
    async def update_last_login(self, user_id: str) -> bool:
        """Actualizar último acceso del usuario"""
        try:
            # Validar formato de ObjectId
            if not ObjectId.is_valid(user_id):
                logger.warning(f"ID de usuario inválido para actualizar último acceso: {user_id}")
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"ultimo_acceso": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error actualizando último acceso para usuario {user_id}: {str(e)}")
            return False