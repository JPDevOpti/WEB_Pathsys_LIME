import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from app.modules.cases.schemas.case import (
    PatientInfo,
    EntityInfo,
    CaseCreate,
    AdditionalNote,
)


def _valid_patient_info(**overrides):
    base = dict(
        patient_code="1-12345678",
        identification_type=1,
        identification_number="12345678",
        name="Juan Pérez",
        age=35,
        gender="Masculino",
        entity_info=EntityInfo(id="ENT-1", name="Entidad Demo"),
        care_type="Ambulatorio",
        observations=None,
    )
    base.update(overrides)
    return base


def test_patient_info_identification_number_min_length_ok():
    data = _valid_patient_info(identification_number="12345")
    obj = PatientInfo(**data)
    assert obj.identification_number == "12345"


def test_patient_info_identification_number_too_short():
    data = _valid_patient_info(identification_number="1234")
    with pytest.raises(ValidationError):
        PatientInfo(**data)


def test_patient_info_identification_number_max_length_ok():
    data = _valid_patient_info(identification_number="123456789012")
    obj = PatientInfo(**data)
    assert obj.identification_number == "123456789012"


def test_patient_info_age_bounds():
    data = _valid_patient_info(age=0)
    assert PatientInfo(**data).age == 0
    data = _valid_patient_info(age=150)
    assert PatientInfo(**data).age == 150
    data = _valid_patient_info(age=-1)
    with pytest.raises(ValidationError):
        PatientInfo(**data)


def test_case_create_additional_notes_validation():
    # additional_notes se valida cuando se use en CaseUpdate/CaseResponse, aquí verificamos estructura válida
    note = AdditionalNote(date=datetime.now(timezone.utc), note="Observación")
    payload = CaseCreate(
        patient_info=PatientInfo(**_valid_patient_info()),
        requesting_physician="Dr. Demo",
        service="Consulta externa",
        samples=[],
        observations=None,
    )
    assert payload.state in ("En proceso", "Por firmar", "Por entregar", "Completado")
    assert note.note == "Observación"