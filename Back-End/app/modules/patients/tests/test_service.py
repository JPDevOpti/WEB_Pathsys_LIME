import pytest
from types import SimpleNamespace
from app.modules.patients.services.patient_service import PatientService
from app.modules.patients.schemas.patient import IdentificationType, PatientResponse, EntityInfo, Gender, CareType


class FakeRepo:
    def __init__(self, db):
        self.collection = SimpleNamespace(database=db)

    async def change_identification(self, old_code, new_type, new_number, cases_collection):
        return {
            "_id": "507f1f77bcf86cd799439011",
            "id": "507f1f77bcf86cd799439011",
            "patient_code": f"{new_type}-{new_number}",
            "identification_type": new_type,
            "identification_number": new_number,
            "first_name": "Juan",
            "first_lastname": "Pérez",
            "birth_date": __import__("datetime").datetime(1990, 1, 1),
            "gender": "Masculino",
            "location": None,
            "entity_info": {"id": "ENT-1", "name": "Entidad Demo"},
            "care_type": "Ambulatorio",
        }


@pytest.mark.asyncio
async def test_service_change_identification_accepts_enum_int_str(monkeypatch):
    # Monkeypatch PatientRepository con FakeRepo
    import app.modules.patients.services.patient_service as svc_mod
    monkeypatch.setattr(svc_mod, "PatientRepository", lambda db: FakeRepo(db))

    service = PatientService(database=SimpleNamespace())

    # Caso 1: Enum
    resp = await service.change_patient_identification("1-111", IdentificationType.CEDULA_CIUDADANIA, "22222")
    assert isinstance(resp, PatientResponse)
    assert resp.patient_code == "1-22222"

    # Caso 2: int
    resp2 = await service.change_patient_identification("1-111", 1, "33333")
    assert resp2.patient_code == "1-33333"

    # Caso 3: str
    resp3 = await service.change_patient_identification("1-111", "1", "44444")
    assert resp3.patient_code == "1-44444"