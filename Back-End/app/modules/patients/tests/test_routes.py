import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.modules.patients.routes.patient_routes import router, get_service
from app.modules.patients.schemas.patient import PatientResponse, EntityInfo


class FakeService:
    async def change_patient_identification(self, patient_code: str, new_identification_type, new_identification_number: str):
        return PatientResponse(
            id="507f1f77bcf86cd799439011",
            patient_code=f"{int(new_identification_type)}-{new_identification_number}",
            identification_type=int(new_identification_type),
            identification_number=new_identification_number,
            first_name="Juan",
            first_lastname="Pérez",
            birth_date=__import__("datetime").date(1990, 1, 1),
            gender="Masculino",
            location=None,
            entity_info=EntityInfo(id="ENT-1", name="Entidad Demo"),
            care_type="Ambulatorio",
        )


def create_app():
    app = FastAPI()
    app.dependency_overrides[get_service] = lambda: FakeService()
    app.include_router(router, prefix="/patients")
    return app


def test_change_identification_route_success():
    app = create_app()
    client = TestClient(app)

    resp = client.put(
        "/patients/1-111/change-identification",
        params={"new_identification_type": 1, "new_identification_number": "22222"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["patient_code"] == "1-22222"
    assert body["gender"] == "Masculino"