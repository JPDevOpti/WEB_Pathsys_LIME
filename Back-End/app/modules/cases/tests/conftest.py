import os
import sys
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

# Asegura que el paquete 'app' se pueda importar durante los tests
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def mock_db():
    class MockDB:
        def __init__(self):
            self.cases = AsyncMock(name="cases_collection")
            self.case_counters = AsyncMock(name="case_counters_collection")
            self.users = AsyncMock(name="users_collection")

    return MockDB()


@pytest.fixture
def sample_case_doc():
    return {
        "_id": "656565656565656565656565",
        "case_code": "2025-00001",
        "patient_info": {
            "patient_code": "1-12345678",
            "identification_type": 1,
            "identification_number": "12345678",
            "name": "Juan Pérez",
            "age": 35,
            "gender": "Masculino",
            "entity_info": {"id": "ENT-1", "name": "Entidad Demo"},
            "care_type": "Ambulatorio",
            "observations": None,
        },
        "requesting_physician": "Dr. Demo",
        "service": "Consulta externa",
        "samples": [
            {"body_region": "Piel", "tests": [{"id": "T-1", "name": "Biopsia", "quantity": 1}]}
        ],
        "state": "En proceso",
        "priority": "Normal",
        "observations": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


class FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, *_args, **_kwargs):
        return self

    def skip(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    async def to_list(self, length=None):
        return self._docs[: length or len(self._docs)]