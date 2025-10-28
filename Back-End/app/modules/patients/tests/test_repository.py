import pytest
from unittest.mock import AsyncMock
from app.modules.patients.repositories.patient_repository import PatientRepository


@pytest.mark.asyncio
async def test_change_identification_updates_cases_patient_info(mock_db, sample_patient_dict):
    repo = PatientRepository(mock_db)

    # Existing patient with old_code
    mock_db.patients.find_one.side_effect = [
        {"_id": sample_patient_dict["_id"]},  # exists for old_code
        None,  # duplicated check for new_code
        {**sample_patient_dict, "patient_code": "1-87654321"},  # fetch updated
    ]

    mock_db.patients.update_one = AsyncMock(return_value=None)
    mock_db.cases.update_many = AsyncMock(return_value=None)

    updated = await repo.change_identification(
        old_code="1-12345678",
        new_identification_type=1,
        new_identification_number="87654321",
        cases_collection=mock_db.cases,
    )

    # Verifica filtro y actualización en cases con la ruta correcta
    mock_db.cases.update_many.assert_awaited()
    args, kwargs = mock_db.cases.update_many.call_args
    assert args[0] == {"patient_info.patient_code": "1-12345678"}
    assert args[1] == {"$set": {"patient_info.patient_code": "1-87654321"}}

    # Verifica el retorno del paciente con nuevo código
    assert updated["patient_code"] == "1-87654321"