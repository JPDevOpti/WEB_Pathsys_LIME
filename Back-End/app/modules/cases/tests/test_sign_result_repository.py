import pytest
from unittest.mock import AsyncMock
from app.modules.cases.repositories.sign_repository import SignRepository
from app.modules.cases.repositories.result_repository import ResultRepository


@pytest.mark.asyncio
async def test_sign_repository_validate_case_can_be_signed(mock_db):
    repo = SignRepository(mock_db)
    # Caso no encontrado
    mock_db.cases.find_one = AsyncMock(return_value=None)
    ok = await repo.validate_case_can_be_signed("2025-00001")
    assert ok is False

    # Caso completado
    mock_db.cases.find_one = AsyncMock(return_value={"state": "Completado"})
    ok = await repo.validate_case_can_be_signed("2025-00001")
    assert ok is False

    # Caso en proceso con patólogo asignado con nombre
    mock_db.cases.find_one = AsyncMock(return_value={"state": "En proceso", "assigned_pathologist": {"name": "Dr. X"}})
    ok = await repo.validate_case_can_be_signed("2025-00001")
    assert ok is True


@pytest.mark.asyncio
async def test_result_repository_validate_case_not_completed(mock_db):
    repo = ResultRepository(mock_db)
    # En proceso
    mock_db.cases.find_one = AsyncMock(return_value={"state": "En proceso"})
    assert await repo.validate_case_not_completed("2025-00001") is True

    # Por firmar
    mock_db.cases.find_one = AsyncMock(return_value={"state": "Por firmar"})
    assert await repo.validate_case_not_completed("2025-00001") is True

    # Por entregar (no permitido)
    mock_db.cases.find_one = AsyncMock(return_value={"state": "Por entregar"})
    assert await repo.validate_case_not_completed("2025-00001") is False

    # Completado (no permitido)
    mock_db.cases.find_one = AsyncMock(return_value={"state": "Completado"})
    assert await repo.validate_case_not_completed("2025-00001") is False