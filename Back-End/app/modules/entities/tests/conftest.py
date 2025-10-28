import os
import sys
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

# Asegura importación del paquete 'app'
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self):
            self.entities = AsyncMock(name="entities_collection")

    return MockDB()


@pytest.fixture
def sample_entity_doc():
    return {
        "_id": "616161616161616161616161",
        "name": "Laboratorio Central",
        "entity_code": "EN-01",
        "notes": "Entidad de referencia",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }