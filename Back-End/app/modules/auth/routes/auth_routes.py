"""Rutas de autenticación"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.schemas.token import RefreshTokenRequest
from app.modules.auth.services.auth_service import AuthService
from app.modules.auth.services.token_service import TokenService
from app.modules.auth.repositories.auth_repository import AuthRepository
from app.core.exceptions import UnauthorizedError, NotFoundError
from app.config.database import get_database
from typing import Dict, Any

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
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    """Iniciar sesión"""
    try:
        return await auth_service.authenticate_user(login_data)
    except (UnauthorizedError, NotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@auth_router.post("/refresh")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Renovar token de acceso"""
    try:
        return await auth_service.refresh_token(refresh_data.refresh_token)
    except (UnauthorizedError, NotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

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
            return {"message": "Sesión cerrada exitosamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al cerrar sesión"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@auth_router.get("/me")
async def get_current_user_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Obtener información del usuario actual"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return {
            "id": user.id,
            "email": user.email,
            "rol": user.rol,
            "activo": user.activo,
            "ultimo_acceso": user.ultimo_acceso
        }
    except (UnauthorizedError, NotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )