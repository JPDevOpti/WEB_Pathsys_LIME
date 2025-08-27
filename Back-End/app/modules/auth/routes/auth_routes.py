"""Rutas de autenticación"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.schemas.token import RefreshTokenRequest
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.services.token_service import TokenService
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError, InternalServerError
from app.config.database import get_database
from typing import Dict, Any
import logging
import time
from collections import defaultdict

# Configurar logger
logger = logging.getLogger(__name__)

# Rate limiting básico para login
LOGIN_ATTEMPTS = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5  # Máximo 5 intentos
LOGIN_WINDOW = 300  # Ventana de 5 minutos (300 segundos)

auth_router = APIRouter()
security = HTTPBearer()

def check_rate_limit(email: str) -> bool:
    """Verificar rate limiting para login"""
    now = time.time()
    attempts = LOGIN_ATTEMPTS[email]
    
    # Limpiar intentos antiguos
    attempts = [attempt for attempt in attempts if now - attempt < LOGIN_WINDOW]
    LOGIN_ATTEMPTS[email] = attempts
    
    # Verificar si excede el límite
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        logger.warning(f"Rate limit excedido para {email}: {len(attempts)} intentos en {LOGIN_WINDOW}s")
        return False
    
    return True

def record_login_attempt(email: str):
    """Registrar intento de login"""
    LOGIN_ATTEMPTS[email].append(time.time())

# Dependencias
async def get_auth_repository() -> AuthRepository:
    """Obtener repositorio de autenticación"""
    db = await get_database()
    return AuthRepository(db)

def get_token_service() -> TokenService:
    """Obtener servicio de tokens"""
    return TokenService()

async def get_auth_service(
    auth_repo: AuthRepository = Depends(get_auth_repository),
    token_service: TokenService = Depends(get_token_service)
) -> AuthService:
    """Obtener servicio de autenticación"""
    return AuthService(auth_repo, token_service)

@auth_router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """Iniciar sesión"""
    # Verificar rate limiting
    if not check_rate_limit(login_data.email):
        logger.warning(f"Rate limit excedido para IP {request.client.host}, email {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de login. Intente nuevamente en 5 minutos."
        )
    
    try:
        # Registrar intento de login
        record_login_attempt(login_data.email)
        
        result = await auth_service.authenticate_user(login_data)
        
        # Si el login es exitoso, limpiar intentos fallidos
        LOGIN_ATTEMPTS[login_data.email].clear()
        
        return result
        
    except (UnauthorizedError, NotFoundError) as e:
        logger.warning(f"Login fallido para {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    except ValueError as e:
        logger.error(f"Error de validación en login: {str(e)}")
        raise BadRequestError(detail="Datos de entrada inválidos")
    except Exception as e:
        logger.error(f"Error interno en login: {str(e)}", exc_info=True)
        raise InternalServerError(detail="Error interno del servidor")

@auth_router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Renovar token de acceso"""
    try:
        return await auth_service.refresh_token(refresh_data.refresh_token)
    except (UnauthorizedError, NotFoundError) as e:
        logger.warning(f"Refresh token fallido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de actualización inválido"
        )
    except ValueError as e:
        logger.error(f"Error de validación en refresh: {str(e)}")
        raise BadRequestError(detail="Token de actualización inválido")
    except Exception as e:
        logger.error(f"Error interno en refresh: {str(e)}", exc_info=True)
        raise InternalServerError(detail="Error interno del servidor")

@auth_router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Cerrar sesión"""
    try:
        token = credentials.credentials
        success = await auth_service.logout(token)
        if success:
            logger.info("Sesión cerrada exitosamente")
            return {"message": "Sesión cerrada exitosamente"}
        else:
            logger.warning("Error al cerrar sesión")
            raise BadRequestError(detail="Error al cerrar sesión")
    except (UnauthorizedError, BadRequestError):
        raise
    except Exception as e:
        logger.error(f"Error interno en logout: {str(e)}", exc_info=True)
        raise InternalServerError(detail="Error interno del servidor")

@auth_router.get("/me")
async def get_current_user_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Obtener información del usuario actual"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        
        # Usar solo campos que existen en la BD
        return {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre or "",
            "rol": user.get_primary_role(),
            "is_active": user.is_active,
            "ultimo_acceso": user.ultimo_acceso
        }
    except (UnauthorizedError, NotFoundError) as e:
        logger.warning(f"Error obteniendo usuario actual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o usuario no encontrado"
        )
    except Exception as e:
        logger.error(f"Error interno obteniendo usuario: {str(e)}", exc_info=True)
        raise InternalServerError(detail="Error interno del servidor")

@auth_router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service: TokenService = Depends(get_token_service)
) -> Dict[str, Any]:
    """Verificar validez del token"""
    try:
        token = credentials.credentials
        payload = await token_service.verify_token(token)
        if payload:
            remaining_time = await token_service.get_token_remaining_time(token)
            return {
                "valid": True,
                "user_id": payload.sub,
                "email": payload.email,
                "username": payload.username,
                "roles": payload.roles,
                "expires_in": remaining_time
            }
        else:
            return {"valid": False}
    except Exception as e:
        logger.error(f"Error verificando token: {str(e)}", exc_info=True)
        raise InternalServerError(detail="Error interno del servidor")