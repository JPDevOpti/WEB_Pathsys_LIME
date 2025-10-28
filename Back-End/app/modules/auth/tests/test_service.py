import pytest
import os
import sys
# Añadir ruta absoluta basada en ubicación del archivo
CURRENT_DIR = os.path.dirname(__file__)
APP_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../../../..", "app"))
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
from datetime import timedelta
from typing import Dict, Any, Optional

from app.modules.auth.services.auth_service import AuthService
from app.config.security import get_password_hash, create_access_token, verify_token
from app.config.settings import settings


class FakeAuthRepository:
    def __init__(self) -> None:
        # Valores en español, nombres de campos en inglés (regla de workspace)
        pwd = get_password_hash("secreto123")
        self.users: Dict[str, Dict[str, Any]] = {
            # 24 hex chars para parecer ObjectId
            "64b64c7e8f0a1b2c3d4e5f60": {
                "_id": "64b64c7e8f0a1b2c3d4e5f60",
                "email": "admin@pathsys.io",
                "password_hash": pwd,
                "name": "Administrador Demo",
                "role": "administrador",
                "is_active": True,
                "administrator_code": "ADM-0001",
            },
            "64b64c7e8f0a1b2c3d4e5f61": {
                "_id": "64b64c7e8f0a1b2c3d4e5f61",
                "email": "inactivo@pathsys.io",
                "password_hash": pwd,
                "name": "Usuario Inactivo",
                "role": "auxiliar",
                "is_active": False,
            },
        }

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        # Búsqueda case-insensitive como el repo real
        for u in self.users.values():
            if u["email"].lower() == email.lower() and u.get("is_active", True):
                return u.copy()
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        u = self.users.get(user_id)
        if not u or not u.get("is_active", True):
            return None
        return u.copy()


@pytest.fixture
def service() -> AuthService:
    return AuthService(FakeAuthRepository())


@pytest.mark.asyncio
async def test_login_success_returns_token_and_user(service: AuthService):
    res = await service.login("admin@pathsys.io", "secreto123")
    assert "token" in res and "user" in res
    token = res["token"]
    user = res["user"]

    assert set(["access_token", "token_type", "expires_in"]).issubset(token.keys())
    assert token["token_type"] == "bearer"
    assert token["expires_in"] == int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())

    assert user["id"] == "64b64c7e8f0a1b2c3d4e5f60"
    assert user["email"] == "admin@pathsys.io"
    assert user["role"] == "administrador"
    assert user["is_active"] is True

    # Verificar que el token decodifica al subject correcto
    subject = verify_token(token["access_token"])
    assert subject == "64b64c7e8f0a1b2c3d4e5f60"


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(service: AuthService):
    with pytest.raises(ValueError):
        await service.login("admin@pathsys.io", "malaClave")


@pytest.mark.asyncio
async def test_login_fails_with_unknown_email(service: AuthService):
    with pytest.raises(ValueError):
        await service.login("noexiste@pathsys.io", "secreto123")


@pytest.mark.asyncio
async def test_login_email_is_case_insensitive(service: AuthService):
    res = await service.login("ADMIN@PATHSYS.IO", "secreto123")
    assert res["user"]["email"] == "admin@pathsys.io"


@pytest.mark.asyncio
async def test_refresh_token_success(service: AuthService):
    data = await service.refresh_token("64b64c7e8f0a1b2c3d4e5f60")
    assert set(["access_token", "token_type", "expires_in"]).issubset(data.keys())
    assert verify_token(data["access_token"]) == "64b64c7e8f0a1b2c3d4e5f60"


@pytest.mark.asyncio
async def test_refresh_token_user_not_found_raises(service: AuthService):
    with pytest.raises(ValueError):
        await service.refresh_token("ffffffffffffffffffffffff")


@pytest.mark.asyncio
async def test_refresh_token_inactive_user_raises(service: AuthService):
    with pytest.raises(ValueError):
        await service.refresh_token("64b64c7e8f0a1b2c3d4e5f61")


@pytest.mark.asyncio
async def test_get_user_public_by_id_success(service: AuthService):
    data = await service.get_user_public_by_id("64b64c7e8f0a1b2c3d4e5f60")
    assert data["id"] == "64b64c7e8f0a1b2c3d4e5f60"
    assert data["email"] == "admin@pathsys.io"
    assert data["role"] == "administrador"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_user_public_by_id_not_found_raises(service: AuthService):
    with pytest.raises(ValueError):
        await service.get_user_public_by_id("ffffffffffffffffffffffff")