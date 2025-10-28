import pytest
from datetime import datetime, timezone

from app.modules.auxiliaries.repositories.auxiliar_repository import AuxiliarRepository
from app.modules.auxiliaries.schemas.auxiliar import AuxiliarCreate, AuxiliarUpdate, AuxiliarSearch
from app.core.exceptions import ConflictError


class _DB:
    def __init__(self, coll):
        self.auxiliaries = coll


@pytest.mark.asyncio
async def test_create_and_get_list_search_update_delete(mock_db, sample_auxiliar_doc):
    repo = AuxiliarRepository(_DB(mock_db.auxiliaries))

    # Crear
    created = await repo.create(AuxiliarCreate(**sample_auxiliar_doc))
    assert created["auxiliar_code"] == sample_auxiliar_doc["auxiliar_code"]
    assert created["auxiliar_name"].startswith("Auxiliar")
    assert created["created_at"] is not None and created["updated_at"] is not None

    # Duplicado por code
    with pytest.raises(ConflictError):
        await repo.create(AuxiliarCreate(**{
            **sample_auxiliar_doc,
            "auxiliar_email": "otro@example.com"
        }))

    # Duplicado por email
    with pytest.raises(ConflictError):
        await repo.create(AuxiliarCreate(**{
            **sample_auxiliar_doc,
            "auxiliar_code": "AUX-002"
        }))

    # Obtener por code
    got = await repo.get_by_auxiliar_code("AUX-001")
    assert got["auxiliar_email"] == sample_auxiliar_doc["auxiliar_email"]

    # Obtener por email
    got2 = await repo.get_by_email(sample_auxiliar_doc["auxiliar_email"])
    assert got2["auxiliar_code"] == "AUX-001"

    # Listar activos
    listed = await repo.list_active()
    assert len(listed) == 1

    # Buscar por q
    res_q = await repo.search(AuxiliarSearch(q="Auxiliar"))
    assert len(res_q) == 1

    # Actualizar
    updated = await repo.update_by_auxiliar_code("AUX-001", {"auxiliar_name": "Actualizado"})
    assert updated and updated["auxiliar_name"] == "Actualizado"

    # Eliminar
    ok = await repo.delete_by_auxiliar_code("AUX-001")
    assert ok is True
    still = await repo.get_by_auxiliar_code("AUX-001")
    assert still is None