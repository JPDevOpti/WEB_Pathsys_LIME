import os
import sys
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

# Ensure the Back-End root is on sys.path so 'app' package imports work
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self):
            self.patients = AsyncMock(name="patients_collection")
            self.cases = AsyncMock(name="cases_collection")

    return MockDB()


@pytest.fixture
def sample_patient_dict():
    return {
        "_id": "507f1f77bcf86cd799439011",
        "patient_code": "1-12345678",
        "identification_type": 1,
        "identification_number": "12345678",
        "first_name": "Juan",
        "second_name": "Carlos",
        "first_lastname": "Pérez",
        "second_lastname": "Gómez",
        "birth_date": datetime(1990, 1, 1),
        "gender": "Masculino",
        "location": None,
        "entity_info": {"id": "ENT-1", "name": "Entidad Demo"},
        "care_type": "Ambulatorio",
        "observations": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }