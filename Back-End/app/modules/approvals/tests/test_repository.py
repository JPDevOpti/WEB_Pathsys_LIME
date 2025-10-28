import pytest
from datetime import datetime, timezone, timedelta

from app.modules.approvals.repositories.approval_repository import ApprovalRepository
from app.modules.approvals.models.approval_request import ApprovalStateEnum
from app.modules.approvals.schemas.approval import ApprovalRequestSearch


@pytest.mark.asyncio
async def test_repository_crud_and_search(mock_db, sample_approval_doc):
    repo = ApprovalRepository(mock_db)

    # Crear inicial directamente en colección para preparar escenario
    await mock_db.approval_requests.insert_one(dict(sample_approval_doc))

    # get_by_approval_code y get_by_original_case_code
    got = await repo.get_by_approval_code("AP-2025-001")
    assert got and got.approval_code == "AP-2025-001"

    got2 = await repo.get_by_original_case_code("2025-00001")
    assert got2 and got2.original_case_code == "2025-00001"

    # search por original_case_code (regex) y estado
    s = await repo.search(ApprovalRequestSearch(original_case_code="2025-000", approval_state=ApprovalStateEnum.REQUEST_MADE))
    assert len(s) == 1 and s[0].approval_code == "AP-2025-001"

    # count con mismo filtro
    c = await repo.count(ApprovalRequestSearch(original_case_code="2025-000", approval_state=ApprovalStateEnum.REQUEST_MADE))
    assert c == 1

    # get_by_state
    by_state = await repo.get_by_state(ApprovalStateEnum.REQUEST_MADE, limit=10)
    assert len(by_state) == 1 and by_state[0].original_case_code == "2025-00001"

    # update_state -> pending_approval
    ok = await repo.update_state("AP-2025-001", ApprovalStateEnum.PENDING_APPROVAL)
    assert ok is True
    after = await repo.get_by_approval_code("AP-2025-001")
    assert after and after.approval_state == ApprovalStateEnum.PENDING_APPROVAL

    # update_complementary_tests
    updated = await repo.update_complementary_tests(
        "AP-2025-001",
        [{"code": "T-202", "name": "Prueba Nueva", "quantity": 1}]
    )
    assert updated and len(updated.complementary_tests) == 1 and updated.complementary_tests[0].code == "T-202"

    # update_by_approval_code
    upd = await repo.update_by_approval_code("AP-2025-001", {"approval_state": ApprovalStateEnum.APPROVED.value})
    assert upd and upd.approval_state == ApprovalStateEnum.APPROVED

    # get_stats
    stats = await repo.get_stats()
    # Con 1 documento en estado approved
    assert stats["total_requests"] >= 1
    assert stats["approved"] >= 1

    # delete_by_approval_code
    deleted = await repo.delete_by_approval_code("AP-2025-001")
    assert deleted is True
    missing = await repo.get_by_approval_code("AP-2025-001")
    assert missing is None

    # Probar búsqueda por rango de fechas en approval_info.request_date
    # Insertar dos documentos con fechas distintas
    now = datetime.now(timezone.utc)
    doc_a = {
        "approval_code": "AP-2025-010",
        "original_case_code": "2025-01010",
        "approval_state": "request_made",
        "complementary_tests": [
            {"code": "T-1", "name": "Prueba A", "quantity": 1}
        ],
        "approval_info": {"reason": "Motivo A", "request_date": now - timedelta(days=2)},
        "created_at": now - timedelta(days=2),
        "updated_at": now - timedelta(days=2),
    }
    doc_b = {
        "approval_code": "AP-2025-011",
        "original_case_code": "2025-01011",
        "approval_state": "request_made",
        "complementary_tests": [
            {"code": "T-2", "name": "Prueba B", "quantity": 1}
        ],
        "approval_info": {"reason": "Motivo B", "request_date": now - timedelta(days=1)},
        "created_at": now - timedelta(days=1),
        "updated_at": now - timedelta(days=1),
    }
    await mock_db.approval_requests.insert_one(doc_a)
    await mock_db.approval_requests.insert_one(doc_b)

    r = await repo.search(ApprovalRequestSearch(request_date_from=now - timedelta(days=1, hours=12)))
    assert len(r) == 1 and r[0].approval_code == "AP-2025-011"