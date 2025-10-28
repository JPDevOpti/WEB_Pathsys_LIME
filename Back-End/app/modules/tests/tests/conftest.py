import os
import sys
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

# Asegura que el paquete 'app' se pueda importar durante los tests
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self):
            self.tests = AsyncMock(name="tests_collection")

    return MockDB()


@pytest.fixture
def sample_test_doc():
    return {
        "_id": "606060606060606060606060",
        "name": "Hematología básica",
        "test_code": "HB-01",
        "description": "Perfil sanguíneo estándar",
        "time": 30,
        "price": 25.5,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }