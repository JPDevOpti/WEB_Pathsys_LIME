import pytest
import os
import sys
# Añadir ruta absoluta basada en ubicación del archivo
CURRENT_DIR = os.path.dirname(__file__)
APP_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "../../../..", "app"))
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional

from app.modules.auth.routes.auth_routes import auth_router
from app.modules.auth.services.auth_service import AuthService
from app.config.security import get_password_hash, create_access_token
from datetime import timedelta


class FakeAuthRepository:
    def __init__(self) -> None:
        pwd = get_password_hash("secreto123")
        self.users: Dict[str, Dict[str, Any]] = {
            "64b64c7e8f0a1b2c3d4e5f60": {
                "_id": "64b64c7e8f0a1b2c3d4e5f60",
                "email": "admin@pathsys.io",
                "password_hash": pwd,
                "name": "Administrador Demo",
                "role": "administrador",
                "is_active": True,
                "administrator_code": "ADM-0001",
            },
            "64b64c7e8f0a1b2c3d4e5f62": {
                "_id": "64b64c7e8f0a1b2c3d4e5f62",
                "email": "otro@pathsys.io",
                "password_hash": pwd,
                "name": "Otro Usuario",
                "role": "auxiliar",
                "is_active": True,
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
def app(monkeypatch):
    async def fake_build():
        return AuthService(FakeAuthRepository())

    # Parchear AuthService.build para evitar acceso a DB real
    monkeypatch.setattr("app.modules.auth.services.auth_service.AuthService.build", fake_build)

    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    return app


def test_login_route_success_200(app):
    client = TestClient(app)
    r = client.post("/auth/login", json={"email": "admin@pathsys.io", "password": "secreto123"})
    assert r.status_code == 200
    body = r.json()
    assert "token" in body and "user" in body
    assert body["token"]["token_type"] == "bearer"
    assert body["user"]["email"] == "admin@pathsys.io"
    assert body["user"]["role"] == "administrador"


def test_login_route_invalid_credentials_401(app):
    client = TestClient(app)
    r = client.post("/auth/login", json={"email": "admin@pathsys.io", "password": "incorrecta"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Credenciales inválidas"


def test_login_route_internal_error_500(monkeypatch):
    # Simular error inesperado en build
    async def exploding_build():
        raise RuntimeError("boom")

    monkeypatch.setattr("app.modules.auth.services.auth_service.AuthService.build", exploding_build)
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    client = TestClient(app)
    r = client.post("/auth/login", json={"email": "admin@pathsys.io", "password": "secreto123"})
    assert r.status_code == 500
    assert r.json()["detail"] == "Error interno de autenticación"


def test_me_requires_valid_token_and_returns_user(app):
    client = TestClient(app)
    token = create_access_token("64b64c7e8f0a1b2c3d4e5f60")
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "64b64c7e8f0a1b2c3d4e5f60"
    assert data["email"] == "admin@pathsys.io"


def test_me_with_invalid_token_returns_401(app):
    client = TestClient(app)
    r = client.get("/auth/me", headers={"Authorization": "Bearer INVALIDO"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated" or r.json()["detail"] == "Token inválido o expirado"


def test_refresh_success_returns_new_token(app):
    client = TestClient(app)
    token = create_access_token("64b64c7e8f0a1b2c3d4e5f60")
    r = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert set(["access_token", "token_type", "expires_in"]).issubset(data.keys())


def test_refresh_with_unknown_user_returns_401(app):
    client = TestClient(app)
    token = create_access_token("ffffffffffffffffffffffff")
    r = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_me_with_expired_token_returns_401(app):
    client = TestClient(app)
    expired = create_access_token("64b64c7e8f0a1b2c3d4e5f60", expires_delta=timedelta(seconds=-1))
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_refresh_with_inactive_user_returns_401(app, monkeypatch):
    # Parchear build para que repo devuelva usuario inactivo para ese id
    class RepoInactive(FakeAuthRepository):
        def __init__(self) -> None:
            super().__init__()
            self.users["64b64c7e8f0a1b2c3d4e5f61"]["is_active"] = False

        async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
            u = self.users.get(user_id)
            if not u or not u.get("is_active", True):
                return None
            return u.copy()

    async def build_inactive():
        return AuthService(RepoInactive())

    monkeypatch.setattr("app.modules.auth.services.auth_service.AuthService.build", build_inactive)
    app2 = FastAPI()
    app2.include_router(auth_router, prefix="/auth")
    client = TestClient(app2)
    token = create_access_token("64b64c7e8f0a1b2c3d4e5f61")
    r = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401