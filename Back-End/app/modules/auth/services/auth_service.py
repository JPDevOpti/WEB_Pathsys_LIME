"""Servicio de autenticación"""

from typing import Optional
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.models.auth import AuthUser
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.services.token_service import TokenService
from app.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from app.shared.schemas.common import RolEnum
from datetime import datetime
import logging

# Configurar logger
logger = logging.getLogger(__name__)


class AuthService:
    """Servicio para lógica de autenticación"""
    
    def __init__(self, auth_repository: AuthRepository, token_service: TokenService):
        self.auth_repository = auth_repository
        self.token_service = token_service
    
    def _validate_roles(self, roles: list) -> list:
        """Validar que los roles sean válidos según RolEnum"""
        valid_roles = []
        valid_role_values = [role.value for role in RolEnum]
        
        for role in roles:
            role_str = role.value if hasattr(role, 'value') else str(role)
            if role_str in valid_role_values:
                valid_roles.append(role_str)
            else:
                logger.warning(f"Rol inválido encontrado: {role_str}")
        
        if not valid_roles:
            logger.warning("No se encontraron roles válidos, usando rol por defecto")
            valid_roles = ["user"]
        
        return valid_roles
    
    async def authenticate_user(self, login_data: LoginRequest) -> LoginResponse:
        """Autenticar usuario y generar token"""
        # Verificar credenciales
        user = await self.auth_repository.get_user_by_email(login_data.email)
        if not user:
            logger.warning(f"Intento de login con email no encontrado: {login_data.email}")
            raise UnauthorizedError("Credenciales inválidas")
        
        # Verificar contraseña
        is_valid = await self.auth_repository.verify_password(
            login_data.email, 
            login_data.password
        )
        if not is_valid:
            logger.warning(f"Intento de login con contraseña incorrecta para: {login_data.email}")
            raise UnauthorizedError("Credenciales inválidas")
        
        # Verificar que el usuario esté activo
        if not user.is_user_active():
            logger.warning(f"Intento de login con usuario inactivo: {login_data.email}")
            raise UnauthorizedError("Usuario inactivo")
        
        # Generar tokens usando métodos del modelo y validar roles
        roles_strings = user.get_all_roles()
        validated_roles = self._validate_roles(roles_strings)
        
        # Generar access token
        token_data = await self.token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            username=user.get_display_name(),
            roles=validated_roles
        )
        
        # Generar refresh token
        refresh_token = await self.token_service.create_refresh_token(
            user_id=user.id,
            email=user.email,
            username=user.get_display_name(),
            roles=validated_roles
        )
        
        # Actualizar último acceso
        await self.auth_repository.update_last_login(user.id)
        
        # Preparar respuesta usando solo campos que existen en la BD
        user_data = {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre or "",
            "rol": user.get_primary_role(),
            "roles": validated_roles
        }
        
        logger.info(f"Login exitoso para usuario: {user.email} con roles: {validated_roles}")
        
        return LoginResponse(
            access_token=token_data["access_token"],
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=token_data["expires_in"],
            user=user_data
        )
    
    async def get_current_user(self, token: str) -> AuthUser:
        """Obtener usuario actual desde token"""
        # Verificar y decodificar token
        payload = await self.token_service.verify_token(token)
        if not payload:
            logger.warning("Intento de acceso con token inválido")
            raise UnauthorizedError("Token inválido")
        
        # Obtener usuario
        user = await self.auth_repository.get_user_by_id(payload.sub)
        if not user:
            logger.warning(f"Usuario no encontrado para token: {payload.sub}")
            raise NotFoundError("Usuario no encontrado")
        
        # Verificar que el usuario esté activo
        if not user.is_user_active():
            logger.warning(f"Intento de acceso con usuario inactivo: {user.email}")
            raise UnauthorizedError("Usuario inactivo")
        
        return user
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Renovar token de acceso"""
        # Verificar refresh token (debe ser de tipo "refresh")
        payload = await self.token_service.verify_token(refresh_token, expected_type="refresh")
        if not payload:
            logger.warning("Intento de refresh con token inválido")
            raise UnauthorizedError("Refresh token inválido")
        
        # Obtener usuario
        user = await self.auth_repository.get_user_by_id(payload.sub)
        if not user:
            logger.warning(f"Usuario no encontrado para refresh token: {payload.sub}")
            raise NotFoundError("Usuario no encontrado")
        
        # Verificar que el usuario esté activo
        if not user.is_user_active():
            logger.warning(f"Intento de refresh con usuario inactivo: {user.email}")
            raise UnauthorizedError("Usuario inactivo")
        
        # Generar nuevo token usando métodos del modelo y validar roles
        roles_strings = user.get_all_roles()
        validated_roles = self._validate_roles(roles_strings)
        
        # Generar nuevo token
        return await self.token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            username=user.get_display_name(),
            roles=validated_roles
        )
    
    async def logout(self, token: str) -> bool:
        """Cerrar sesión (invalidar token)"""
        try:
            # En una implementación real, se agregaría el token a una blacklist
            # Por ahora, simplemente retornamos True
            logger.info("Logout exitoso")
            return True
        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            return False