from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config.security import verify_token
from app.modules.auth.schemas.login import LoginRequest, LoginResponse
from app.modules.auth.services.auth_service import AuthService


auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@auth_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    try:
        service = await AuthService.build()
        result = await service.login(payload.email, payload.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno de autenticación")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    subject = verify_token(token)
    if subject is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return subject


@auth_router.get("/me")
async def me(user_id: str = Depends(get_current_user_id)):
    try:
        service = await AuthService.build()
        user = await service.get_user_public_by_id(user_id)
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno")


