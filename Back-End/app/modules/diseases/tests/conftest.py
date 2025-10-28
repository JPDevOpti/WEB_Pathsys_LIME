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
            self.diseases = AsyncMock(name="diseases_collection")

    return MockDB()


@pytest.fixture
def sample_disease_doc():
    # Campos en inglés, valores en español
    return {
        "_id": "507f1f77bcf86cd799439011",
        "table": "CIE10",
        "code": "A000",
        "name": "CÓLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
        "description": "CÓLERA",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }