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
            self.residents = AsyncMock(name="residents_collection")
            self.users = AsyncMock(name="users_collection")

    return MockDB()


@pytest.fixture
def sample_resident_doc():
    return {
        "_id": "656565656565656565656565",
        "resident_code": "R-0001",
        "resident_name": "Dr. Residente Demo",
        "initials": "DRD",
        "resident_email": "residente@pathsys.io",
        "medical_license": "RML-12345",
        "is_active": True,
        "observations": "Activo en patología general",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }