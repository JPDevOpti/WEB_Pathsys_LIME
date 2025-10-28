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
            self.tickets = AsyncMock(name="tickets_collection")
            self.consecutive_tickets = AsyncMock(name="consecutive_tickets_collection")

        def __getitem__(self, name: str):
            # Soporta acceso estilo database["tickets"]
            return getattr(self, name)

    return MockDB()


@pytest.fixture
def sample_ticket_doc():
    # Campos en inglés, valores en español (cuando aplique)
    return {
        "_id": "507f1f77bcf86cd799439012",
        "ticket_code": "T-2025-001",
        "title": "Fallo en carga de imágenes",
        "category": "technical",
        "description": "No se pueden cargar imágenes en el formulario",
        "image": None,
        "ticket_date": datetime.now(timezone.utc),
        "status": "open",
        "created_by": "user-123",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }