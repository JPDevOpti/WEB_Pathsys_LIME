"""Configuración de pytest para WEB-LIS PathSys"""

import pytest
import asyncio
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import get_database
from app.config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Crear un event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Crear una base de datos de test"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[f"{settings.DATABASE_NAME}_test"]
    
    yield db
    
    # Limpiar después de los tests
    await client.drop_database(f"{settings.DATABASE_NAME}_test")
    client.close()


@pytest.fixture
def client() -> TestClient:
    """Cliente de test para FastAPI"""
    return TestClient(app)


@pytest.fixture
async def auth_headers(client: TestClient) -> dict:
    """Headers de autenticación para tests"""
    # Aquí se implementaría la lógica para obtener un token de test
    # Por ahora retornamos headers vacíos
    return {}


@pytest.fixture(autouse=True)
async def clean_db(test_db):
    """Limpiar la base de datos antes de cada test"""
    # Limpiar todas las colecciones antes de cada test
    collections = await test_db.list_collection_names()
    for collection in collections:
        await test_db[collection].delete_many({})
    
    yield
    
    # Limpiar después del test si es necesario
    pass