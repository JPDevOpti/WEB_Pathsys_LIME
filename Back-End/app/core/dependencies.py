from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.config.security import verify_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.modules.auth.models.auth import AuthUser
from app.modules.auth.repositories.auth_repository import AuthRepository

# Configurar esquema de autenticación
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> AuthUser:
    """Obtener usuario actual desde el token JWT"""
    
    # Verificar token
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise UnauthorizedError(detail="Token inválido")
    
    # Buscar usuario en la base de datos
    user_repo = AuthRepository(db)
    user = await user_repo.get_user_by_id(user_id)
    
    if not user:
        raise UnauthorizedError(detail="Usuario no encontrado")
    
    if not user.activo:
        raise UnauthorizedError(detail="Usuario inactivo")
    
    return user

async def get_current_active_user(
    current_user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """Obtener usuario activo actual"""
    if not current_user.activo:
        raise UnauthorizedError(detail="Usuario inactivo")
    return current_user

def require_roles(allowed_roles: List[str]):
    """Decorator para requerir roles específicos"""
    def role_checker(current_user: AuthUser = Depends(get_current_active_user)):
        if current_user.rol not in allowed_roles:
            raise ForbiddenError(
                detail=f"Acceso denegado. Roles requeridos: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Dependencias específicas por rol
def require_admin(current_user: AuthUser = Depends(get_current_active_user)) -> AuthUser:
    """Requerir rol de administrador"""
    if current_user.rol != "admin":
        raise ForbiddenError(detail="Acceso denegado. Se requiere rol de administrador")
    return current_user

def require_patologo(current_user: AuthUser = Depends(get_current_active_user)) -> AuthUser:
    """Requerir rol de patólogo"""
    if current_user.rol not in ["admin", "patologo"]:
        raise ForbiddenError(detail="Acceso denegado. Se requiere rol de patólogo")
    return current_user

def require_recepcionista(current_user: AuthUser = Depends(get_current_active_user)) -> AuthUser:
    """Requerir rol de recepcionista"""
    if current_user.rol not in ["admin", "recepcionista"]:
        raise ForbiddenError(detail="Acceso denegado. Se requiere rol de recepcionista")
    return current_user

# Dependencia opcional para usuario
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Optional[AuthUser]:
    """Obtener usuario actual de forma opcional (puede ser None)"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None