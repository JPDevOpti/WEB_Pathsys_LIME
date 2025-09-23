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

# Configurar logger
logger = logging.getLogger(__name__)

auth_router = APIRouter()
security = HTTPBearer()

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
    try:
        result = await auth_service.authenticate_user(login_data)
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
        
        primary_role = user.get_primary_role()
        # Usar solo campos que existen en la BD
        response = {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre or "",
            "rol": primary_role,
            "is_active": user.is_active,
            "ultimo_acceso": user.ultimo_acceso,
            "patologo_code": getattr(user, "patologo_code", None),
            "auxiliar_code": getattr(user, "auxiliar_code", None),
            "residente_code": getattr(user, "residente_code", None),
            "administrador_code": getattr(user, "administrador_code", None),
            "facturacion_code": getattr(user, "facturacion_code", None),
            "role_code": getattr(user, f"{primary_role}_code", None)
        }
        logger.info(
            f"/auth/me | user={user.email} rol={primary_role} role_code={response.get('role_code')}"
        )
        return response
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