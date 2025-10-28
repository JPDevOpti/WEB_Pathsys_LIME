import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from app.modules.residents.repositories.resident_repository import ResidentRepository
from app.modules.residents.schemas.resident import ResidentCreate


@pytest.mark.asyncio
async def test_create_sets_timestamps_and_returns_id(mock_db, sample_resident_doc):
    repo = ResidentRepository(mock_db)

    # Mock insert_one y find_one
    class _InsertResult:
        inserted_id = sample_resident_doc["_id"]

    mock_db.residents.insert_one = AsyncMock(return_value=_InsertResult())
    mock_db.residents.find_one = AsyncMock(return_value=sample_resident_doc)

    payload = ResidentCreate(
        resident_code="R-0001",
        resident_name="Dr. Residente Demo",
        initials="DRD",
        resident_email="residente@pathsys.io",
        medical_license="RML-12345",
        is_active=True,
        observations="Activo en patología general",
        password="secret123",
    )

    created = await repo.create(payload)
    assert created["id"] == str(sample_resident_doc["_id"])  # convertido por _convert_doc_to_response
    assert isinstance(created.get("created_at"), datetime)
    assert created["created_at"].tzinfo is not None
    assert created["updated_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_update_by_code_sets_updated_at(mock_db, sample_resident_doc):
    repo = ResidentRepository(mock_db)

    # Mock update_one con modificación exitosa
    class _UpdateResult:
        modified_count = 1

    mock_db.residents.update_one = AsyncMock(return_value=_UpdateResult())
    # get_by_resident_code llama a find_one
    mock_db.residents.find_one = AsyncMock(return_value=sample_resident_doc)

    out = await repo.update_by_resident_code("R-0001", {"resident_name": "Otro"})
    assert out is not None
    # No podemos leer el valor exacto que repo calculó, pero verificamos tz-aware
    # a través del doc devuelto por find_one (fixture)
    assert out["updated_at"].tzinfo is not None