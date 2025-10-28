import pytest
from datetime import datetime, timezone

from app.modules.billing.repositories.billing_repository import BillingRepository
from app.core.exceptions import ConflictError


@pytest.mark.asyncio
async def test_create_and_get_list_search_update_delete(mock_db, sample_billing_doc):
    repo = BillingRepository(mock_db)

    # Pre-cargar un documento y verificar get_by_* y list_active
    await mock_db.billing.insert_one(sample_billing_doc)

    got = await repo.get_by_billing_code("FAC-001")
    assert got and got["billing_name"].startswith("Usuario") and got["id"]

    by_email = await repo.get_by_email("usuario.facturacion@example.com")
    assert by_email and by_email["billing_code"] == "FAC-001"

    lst = await repo.list_active()
    assert len(lst) == 1

    # search general q
    from app.modules.billing.schemas.billing import BillingSearch
    s = await repo.search(BillingSearch(q="Usuario"))
    assert len(s) == 1

    # create nuevo y probar duplicados
    from app.modules.billing.schemas.billing import BillingCreate
    payload = BillingCreate(
        billing_code="FAC-002",
        billing_name="Otro Usuario",
        billing_email="otro.usuario@example.com",
        is_active=True,
        observations="Nueva observación",
        password="secreta123",
    )
    created = await repo.create(payload)
    assert created["billing_code"] == "FAC-002" and created["created_at"] and created["updated_at"]

    # Duplicado por código
    with pytest.raises(ConflictError):
        await repo.create(BillingCreate(
            billing_code="FAC-002",
            billing_name="Duplicado",
            billing_email="nuevo@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))

    # Duplicado por email
    with pytest.raises(ConflictError):
        await repo.create(BillingCreate(
            billing_code="FAC-003",
            billing_name="Duplicado Email",
            billing_email="otro.usuario@example.com",
            is_active=True,
            observations=None,
            password="abc12345"
        ))

    # update por código
    updated = await repo.update_by_billing_code("FAC-002", {"billing_name": "Nombre Actualizado"})
    assert updated and updated["billing_name"] == "Nombre Actualizado" and updated["updated_at"]

    # delete por código
    ok = await repo.delete_by_billing_code("FAC-002")
    assert ok is True