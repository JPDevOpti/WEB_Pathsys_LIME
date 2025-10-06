from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from typing import Optional
from app.config.security import verify_token
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.services.auth_service import AuthService


auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer(auto_error=False)


@auth_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    try:
        service = await AuthService.build()
        result = await service.login(payload.email, payload.password)
        return result
    except ValueError:
        # Evitar filtrar detalles internos como avisos de longitud de bcrypt
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal authentication error")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    subject = verify_token(token)
    if subject is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return subject


async def get_current_user_id_optional(credentials = Depends(http_bearer)) -> Optional[str]:
    """Obtener user_id del token si existe y es válido, o None si no hay token/expiró"""
    if not credentials:
        return None
    
    try:
        subject = verify_token(credentials.credentials)
        return subject
    except Exception:
        return None


@auth_router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    try:
        service = await AuthService.build()
        user = await service.get_user_public_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal error")


