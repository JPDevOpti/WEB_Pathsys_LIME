import os
import sys
import pytest
from datetime import datetime, timezone

# Asegura que el paquete 'app' se pueda importar durante los tests
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture
def sample_pathologist_doc():
    return {
        "_id": "656565656565656565656565",
        "pathologist_code": "P-0001",
        "pathologist_name": "Dra. Demo",
        "initials": "DD",
        "pathologist_email": "demo@pathsys.io",
        "medical_license": "ML-12345",
        "is_active": True,
        "signature": "/uploads/signatures/P-0001.png",
        "observations": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }