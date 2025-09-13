"""Servicio compartido para gestión de usuarios"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.security import get_password_hash
from datetime import datetime, timezone
from bson import ObjectId


class UserManagementService:
    """Servicio para operaciones de gestión de usuarios"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.usuarios_collection = self.db.usuarios
    
    async def create_user_for_pathologist(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Crear un usuario en la colección usuarios para un patólogo
        
        Args:
            name: Nombre completo del patólogo
            email: Email del patólogo
            password: Contraseña en texto plano
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        return await self._create_user_with_role(name, email, password, "patologo", is_active)
    
    async def create_user_for_auxiliary(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Crear un usuario en la colección usuarios para un auxiliar
        
        Args:
            name: Nombre completo del auxiliar
            email: Email del auxiliar
            password: Contraseña en texto plano
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        return await self._create_user_with_role(name, email, password, "auxiliar", is_active)
    
    async def create_user_for_resident(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Crear un usuario en la colección usuarios para un residente
        
        Args:
            name: Nombre completo del residente
            email: Email del residente
            password: Contraseña en texto plano
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        return await self._create_user_with_role(name, email, password, "residente", is_active)
    
    async def create_user_for_administrator(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Crear un usuario en la colección usuarios para un administrador
        
        Args:
            name: Nombre completo del administrador
            email: Email del administrador
            password: Contraseña en texto plano
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        return await self._create_user_with_role(name, email, password, "administrador", is_active)
    
    async def create_user_for_facturacion(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Crear un usuario en la colección usuarios para facturación
        
        Args:
            name: Nombre completo del usuario de facturación
            email: Email del usuario de facturación
            password: Contraseña en texto plano
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        print(f"🔧 Creando usuario de facturación: {name} ({email}) con rol 'facturacion'")
        result = await self._create_user_with_role(name, email, password, "facturacion", is_active)
        print(f"✅ Usuario de facturación creado: {result}")
        return result
    
    async def _create_user_with_role(
        self,
        name: str,
        email: str,
        password: str,
        role: str,
        is_active: bool = True
    ) -> Optional[dict]:
        """
        Método privado para crear usuarios con un rol específico
        
        Args:
            name: Nombre completo del usuario
            email: Email del usuario
            password: Contraseña en texto plano
            role: Rol del usuario (patologo, auxiliar, etc.)
            is_active: Estado activo del usuario
            
        Returns:
            dict: Documento del usuario creado o None si falla
        """
        try:
            # Verificar que el email no esté ya en uso
            existing_user = await self.usuarios_collection.find_one({"email": email})
            if existing_user:
                raise ValueError(f"Ya existe un usuario con el email {email}")
            
            # Hashear la contraseña
            password_hash = get_password_hash(password)
            
            # Crear documento del usuario
            user_document = {
                "nombre": name,
                "email": email,
                "rol": role,
                "password_hash": password_hash,
                "is_active": is_active,
                "fecha_creacion": datetime.now(timezone.utc),
                "fecha_actualizacion": datetime.now(timezone.utc)
            }
            
            print(f"🔧 Documento de usuario a crear: {user_document}")
            
            # Insertar en la base de datos
            result = await self.usuarios_collection.insert_one(user_document)
            
            # Retornar el documento creado con el ID
            created_user = await self.usuarios_collection.find_one({"_id": result.inserted_id})
            if created_user:
                created_user["id"] = str(created_user["_id"])
                del created_user["_id"]
                # No incluir password_hash en la respuesta
                if "password_hash" in created_user:
                    del created_user["password_hash"]
            
            return created_user
            
        except Exception as e:
            print(f"Error creating user with role {role}: {e}")
            raise e
    
    async def check_email_exists_in_users(self, email: str) -> bool:
        """
        Verificar si un email ya existe en la colección usuarios
        
        Args:
            email: Email a verificar
            
        Returns:
            bool: True si existe, False si no existe
        """
        try:
            existing_user = await self.usuarios_collection.find_one({"email": email})
            return existing_user is not None
        except Exception:
            return False
    
    async def delete_user_by_email(self, email: str) -> bool:
        """
        Eliminar un usuario por email (usado para rollback)
        
        Args:
            email: Email del usuario a eliminar
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        try:
            result = await self.usuarios_collection.delete_one({"email": email})
            return result.deleted_count > 0
        except Exception:
            return False

    async def update_user_for_resident(
        self,
        old_email: str,
        *,
        name: Optional[str] = None,
        new_email: Optional[str] = None,
        is_active: Optional[bool] = None,
        new_password: Optional[str] = None
    ) -> bool:
        """
        Actualiza el documento del usuario asociado a un residente en la colección usuarios.

        - Busca al usuario por el email anterior (old_email)
        - Si se especifica new_email y es diferente, valida que no exista en usuarios
        - Actualiza los campos provistos: nombre, email, is_active y fecha_actualizacion
        """
        try:
            # Buscar usuario por old_email
            user = await self.usuarios_collection.find_one({"email": old_email})
            # Si no existe, intentar por new_email (si se cambió)
            if not user and new_email:
                user = await self.usuarios_collection.find_one({"email": new_email})
            # Intento final tolerante a mayúsculas/minúsculas
            if not user:
                user = await self.usuarios_collection.find_one({
                    "email": {"$regex": f"^{(new_email or old_email)}$", "$options": "i"}
                })
            if not user:
                # No hay usuario asociado; no lo creamos aquí (no tenemos password)
                return False

            update_doc = {"$set": {"fecha_actualizacion": datetime.utcnow()}}

            if name is not None:
                update_doc["$set"]["nombre"] = name

            if is_active is not None:
                update_doc["$set"]["is_active"] = is_active

            if new_email is not None and new_email != old_email:
                # Validar que el nuevo email no esté ya en uso por otro usuario
                exists = await self.usuarios_collection.find_one({"email": new_email})
                if exists and str(exists.get("_id")) != str(user.get("_id")):
                    raise ValueError("El nuevo email ya está registrado en usuarios")
                update_doc["$set"]["email"] = new_email

            if new_password:
                update_doc["$set"]["password_hash"] = get_password_hash(new_password)

            result = await self.usuarios_collection.update_one({"_id": user["_id"]}, update_doc)
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error updating user for resident: {e}")
            raise e

    async def update_user_for_auxiliary(
        self,
        old_email: str,
        *,
        name: Optional[str] = None,
        new_email: Optional[str] = None,
        is_active: Optional[bool] = None,
        new_password: Optional[str] = None
    ) -> bool:
        """
        Actualiza el documento del usuario asociado a un auxiliar en la colección usuarios.

        Lógica paralela a residentes: busca por old_email (o new_email si cambió),
        valida colisiones de email, actualiza nombre, email, is_active y password_hash.
        """
        try:
            user = await self.usuarios_collection.find_one({"email": old_email})
            if not user and new_email:
                user = await self.usuarios_collection.find_one({"email": new_email})
            if not user:
                user = await self.usuarios_collection.find_one({
                    "email": {"$regex": f"^{(new_email or old_email)}$", "$options": "i"}
                })
            if not user:
                return False

            update_doc = {"$set": {"fecha_actualizacion": datetime.utcnow()}}

            if name is not None:
                update_doc["$set"]["nombre"] = name

            if is_active is not None:
                update_doc["$set"]["is_active"] = is_active

            if new_email is not None and new_email != old_email:
                exists = await self.usuarios_collection.find_one({"email": new_email})
                if exists and str(exists.get("_id")) != str(user.get("_id")):
                    raise ValueError("El nuevo email ya está registrado en usuarios")
                update_doc["$set"]["email"] = new_email

            if new_password:
                update_doc["$set"]["password_hash"] = get_password_hash(new_password)

            result = await self.usuarios_collection.update_one({"_id": user["_id"]}, update_doc)
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error updating user for auxiliary: {e}")
            raise e

    async def update_user_for_facturacion(
        self,
        old_email: str,
        *,
        name: Optional[str] = None,
        new_email: Optional[str] = None,
        is_active: Optional[bool] = None,
        new_password: Optional[str] = None
    ) -> bool:
        """
        Actualiza el documento del usuario asociado a facturación en la colección usuarios.

        Lógica paralela a auxiliares: busca por old_email (o new_email si cambió),
        valida colisiones de email, actualiza nombre, email, is_active y password_hash.
        """
        try:
            user = await self.usuarios_collection.find_one({"email": old_email})
            if not user and new_email:
                user = await self.usuarios_collection.find_one({"email": new_email})
            if not user:
                user = await self.usuarios_collection.find_one({
                    "email": {"$regex": f"^{(new_email or old_email)}$", "$options": "i"}
                })
            if not user:
                return False

            update_doc = {"$set": {"fecha_actualizacion": datetime.utcnow()}}

            if name is not None:
                update_doc["$set"]["nombre"] = name

            if is_active is not None:
                update_doc["$set"]["is_active"] = is_active

            if new_email is not None and new_email != old_email:
                exists = await self.usuarios_collection.find_one({"email": new_email})
                if exists and str(exists.get("_id")) != str(user.get("_id")):
                    raise ValueError("El nuevo email ya está registrado en usuarios")
                update_doc["$set"]["email"] = new_email

            if new_password:
                update_doc["$set"]["password_hash"] = get_password_hash(new_password)

            result = await self.usuarios_collection.update_one({"_id": user["_id"]}, update_doc)
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error updating user for facturacion: {e}")
            raise e

    async def update_user(
        self,
        old_email: str,
        *,
        name: Optional[str] = None,
        new_email: Optional[str] = None,
        is_active: Optional[bool] = None,
        new_password: Optional[str] = None
    ) -> bool:
        """
        Actualizar un usuario genérico en la colección usuarios
        
        Args:
            old_email: Email actual del usuario
            name: Nuevo nombre (opcional)
            new_email: Nuevo email (opcional)
            is_active: Nuevo estado activo (opcional)
            new_password: Nueva contraseña (opcional)
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            user = await self.usuarios_collection.find_one({"email": old_email})
            if not user:
                raise ValueError("Usuario no encontrado")

            update_doc = {"$set": {}}

            if name is not None:
                update_doc["$set"]["nombre"] = name

            if is_active is not None:
                update_doc["$set"]["is_active"] = is_active

            if new_email is not None and new_email != old_email:
                # Validar que el nuevo email no esté ya en uso por otro usuario
                exists = await self.usuarios_collection.find_one({"email": new_email})
                if exists and str(exists.get("_id")) != str(user.get("_id")):
                    raise ValueError("El nuevo email ya está registrado en usuarios")
                update_doc["$set"]["email"] = new_email

            if new_password:
                update_doc["$set"]["password_hash"] = get_password_hash(new_password)

            result = await self.usuarios_collection.update_one({"_id": user["_id"]}, update_doc)
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            raise e
