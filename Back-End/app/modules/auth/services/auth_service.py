"""Servicio de autenticación"""

from typing import Optional
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.modules.auth.models.auth import AuthUser
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.services.token_service import TokenService
from app.core.exceptions import UnauthorizedError, NotFoundError
from datetime import datetime


class AuthService:
    """Servicio para lógica de autenticación"""
    
    def __init__(self, auth_repository: AuthRepository, token_service: TokenService):
        self.auth_repository = auth_repository
        self.token_service = token_service
    
    async def authenticate_user(self, login_data: LoginRequest) -> LoginResponse:
        """Autenticar usuario y generar token"""
        # Verificar credenciales
        user = await self.auth_repository.get_user_by_email(login_data.email)
        if not user:
            raise UnauthorizedError("Credenciales inválidas")
        
        # Verificar contraseña
        is_valid = await self.auth_repository.verify_password(
            login_data.email, 
            login_data.password
        )
        if not is_valid:
            raise UnauthorizedError("Credenciales inválidas")
        
        # Generar token
        user_roles = user.roles or [user.rol] if user.rol else ['user']
        # Convertir roles a strings si son enums
        roles_strings = []
        for role in user_roles:
            if hasattr(role, 'value'):
                roles_strings.append(role.value)
            else:
                roles_strings.append(str(role))
        
        token_data = await self.token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            username=user.username or user.email,
            roles=roles_strings
        )
        
        # Actualizar último acceso
        await self.auth_repository.update_last_login(user.id)
        
        # Preparar respuesta
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username or user.email,
            "nombres": user.nombres or "",
            "apellidos": user.apellidos or "",
            "roles": roles_strings
        }
        
        return LoginResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=token_data["expires_in"],
            user=user_data
        )
    
    async def get_current_user(self, token: str) -> AuthUser:
        """Obtener usuario actual desde token"""
        # Verificar y decodificar token
        payload = await self.token_service.verify_token(token)
        if not payload:
            raise UnauthorizedError("Token inválido")
        
        # Obtener usuario
        user = await self.auth_repository.get_user_by_id(payload.sub)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        
        return user
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """Renovar token de acceso"""
        # Verificar refresh token
        payload = await self.token_service.verify_token(refresh_token)
        if not payload:
            raise UnauthorizedError("Refresh token inválido")
        
        # Obtener usuario
        user = await self.auth_repository.get_user_by_id(payload.sub)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        
        # Generar nuevo token
        return await self.token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            username=user.username,
            roles=[role.value for role in user.roles]
        )
    
    async def logout(self, token: str) -> bool:
        """Cerrar sesión (invalidar token)"""
        # En una implementación real, se agregaría el token a una blacklist
        # Por ahora, simplemente retornamos True
        return True