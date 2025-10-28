import pytest
from datetime import date
from app.modules.patients.schemas.patient import (
    PatientCreate, Gender, CareType, IdentificationType, EntityInfo
)


def test_identification_number_cleaning_and_length():
    data = {
        "identification_type": IdentificationType.CEDULA_CIUDADANIA,
        "identification_number": " 12-34 56 ",
        "first_name": "juan",
        "second_name": "carlos",
        "first_lastname": "perez",
        "second_lastname": "gomez",
        "birth_date": date(1990, 1, 1),
        "gender": Gender.MASCULINO,
        "entity_info": EntityInfo(id="ENT-1", name="Entidad Demo"),
        "care_type": CareType.AMBULATORIO,
        "patient_code": "1-123456",
        "location": None,
    }
    p = PatientCreate(**data)
    assert p.identification_number == "123456"


def test_names_normalization_and_allowed_characters():
    data = {
        "identification_type": IdentificationType.CEDULA_CIUDADANIA,
        "identification_number": "12345678",
        "first_name": " juan p. ",
        "first_lastname": " de-la o'brien ",
        "birth_date": date(1990, 1, 1),
        "gender": Gender.MASCULINO,
        "entity_info": EntityInfo(id="ENT-1", name="Entidad Demo"),
        "care_type": CareType.AMBULATORIO,
        "patient_code": "1-12345678",
        "location": None,
    }
    p = PatientCreate(**data)
    assert p.first_name == "Juan P."
    assert p.first_lastname == "De-La O'Brien"


def test_location_optional_in_schema():
    data = {
        "identification_type": IdentificationType.CEDULA_CIUDADANIA,
        "identification_number": "12345678",
        "first_name": "Juan",
        "first_lastname": "Pérez",
        "birth_date": date(1990, 1, 1),
        "gender": Gender.MASCULINO,
        "entity_info": EntityInfo(id="ENT-1", name="Entidad Demo"),
        "care_type": CareType.AMBULATORIO,
        "patient_code": "1-12345678",
        # No location
    }
    p = PatientCreate(**data)
    assert p.location is None


def test_spanish_values_for_enums():
    assert Gender.MASCULINO.value == "Masculino"
    assert CareType.AMBULATORIO.value == "Ambulatorio"