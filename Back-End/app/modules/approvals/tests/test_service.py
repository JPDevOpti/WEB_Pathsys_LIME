import pytest
import types
from datetime import datetime, timezone

from app.modules.approvals.services.approval_service import ApprovalService
from app.modules.approvals.models.approval_request import ApprovalStateEnum, ApprovalRequest
from app.modules.approvals.schemas.approval import (
    ApprovalRequestCreate,
    ApprovalRequestUpdate,
    ApprovalRequestSearch,
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError


class FakeApprovalRepo:
    def __init__(self):
        self.by_code = {}
        self.by_case = {}
        self._seq = 1

    def _gen_oid(self) -> str:
        # 24 hex chars
        suffix = f"{self._seq % 256:02x}"
        self._seq += 1
        return "507f1f77bcf86cd7994390" + suffix

    async def create(self, data: dict):
        # Ensure a valid ObjectId-like id for validation
        if not data.get("id"):
            data["id"] = self._gen_oid()
        code_key = str(data["approval_code"]).strip()
        self.by_code[code_key] = dict(data)
        self.by_case[data["original_case_code"]] = data["approval_code"]
        return ApprovalRequest.model_validate(data)

    async def get_by_approval_code(self, approval_code: str):
        d = self.by_code.get(approval_code)
        return ApprovalRequest.model_validate(d) if d else None

    async def get_by_original_case_code(self, case_code: str):
        ap_code = self.by_case.get(case_code)
        return await self.get_by_approval_code(ap_code) if ap_code else None

    async def search(self, search_params, skip, limit):
        res = []
        for v in self.by_code.values():
            ok = True
            if search_params.original_case_code and search_params.original_case_code not in v["original_case_code"]:
                ok = False
            if search_params.approval_state and v["approval_state"] != search_params.approval_state:
                ok = False
            if ok:
                res.append(ApprovalRequest.model_validate(v))
        return res[:limit]

    async def count(self, search_params):
        c = 0
        for v in self.by_code.values():
            ok = True
            if search_params.original_case_code and search_params.original_case_code not in v["original_case_code"]:
                ok = False
            if search_params.approval_state and v["approval_state"] != search_params.approval_state:
                ok = False
            if ok:
                c += 1
        return c

    async def get_by_state(self, state, limit):
        res = [ApprovalRequest.model_validate(v) for v in self.by_code.values() if v["approval_state"] == state]
        return res[:limit]

    async def update_state(self, approval_code, new_state):
        key = str(approval_code).strip()
        d = self.by_code.get(key)
        print(f"update_state called with {approval_code}, found={bool(d)}")
        if not d:
            return False
        d["approval_state"] = new_state
        d["updated_at"] = datetime.now(timezone.utc)
        return True

    async def update_by_approval_code(self, approval_code, update_data):
        d = self.by_code.get(approval_code)
        if not d:
            return None
        d.update(update_data)
        d["updated_at"] = datetime.now(timezone.utc)
        return ApprovalRequest.model_validate(d)

    async def update_complementary_tests(self, approval_code, tests):
        return await self.update_by_approval_code(approval_code, {"complementary_tests": tests})

    async def delete_by_approval_code(self, approval_code):
        if approval_code in self.by_code:
            case_code = self.by_code[approval_code]["original_case_code"]
            self.by_code.pop(approval_code, None)
            self.by_case.pop(case_code, None)
            return True
        return False

    async def get_stats(self):
        stats = {"total_requests": 0, "requests_made": 0, "pending_approval": 0, "approved": 0, "rejected": 0}
        for v in self.by_code.values():
            stats["total_requests"] += 1
            if v["approval_state"] == ApprovalStateEnum.REQUEST_MADE:
                stats["requests_made"] += 1
            elif v["approval_state"] == ApprovalStateEnum.PENDING_APPROVAL:
                stats["pending_approval"] += 1
            elif v["approval_state"] == ApprovalStateEnum.APPROVED:
                stats["approved"] += 1
            elif v["approval_state"] == ApprovalStateEnum.REJECTED:
                stats["rejected"] += 1
        return stats


class FakeApprovalConsecutiveRepo:
    def __init__(self):
        self.n = 0

    async def generate_approval_code(self):
        from datetime import datetime, timezone
        self.n += 1
        year = datetime.now(timezone.utc).year
        return f"AP-{year}-{self.n:03d}"


class FakeCaseRepo:
    def __init__(self, exists_case_codes=None):
        self.exists_case_codes = set(exists_case_codes or [])
        self.created = []
        self.updated = []

    async def get_by_case_code(self, case_code: str):
        if case_code in self.exists_case_codes:
            # valores en español, nombres de campos en inglés (esquema válido)
            return {
                "case_code": case_code,
                "patient_info": {
                    "patient_code": "P-001",
                    "name": "Juan Pérez",
                    "age": 45,
                    "gender": "Masculino",
                    "entity_info": {"id": "E1", "name": "Entidad X"},
                    "care_type": "Ambulatorio",
                    "observations": "Caso original",
                },
                "samples": [{"body_region": "General"}],
                "assigned_pathologist": {"id": "pat-1", "name": "Dra. García"},
                "priority": "Normal",
            }
        return None

    async def create(self, data: dict):
        self.created.append(dict(data))
        return dict(data)

    async def update_by_case_code(self, code: str, update_data: dict):
        self.updated.append((code, dict(update_data)))
        return True


class FakeCaseConsecutive:
    def __init__(self):
        self.n = 100

    async def generate_case_code(self, year: int):
        self.n += 1
        return f"{year}-{self.n:05d}"


class _DummyDB:
    def __init__(self):
        self.approval_requests = object()
        self.cases = object()
        self.approval_counters = object()
        self.case_counters = object()
    def __getitem__(self, name: str):
        return getattr(self, name, object())


@pytest.mark.asyncio
async def test_service_full_flow_create_manage_approve_reject_update_delete():
    svc = ApprovalService(_DummyDB())
    # Inyectar fakes
    svc.repository = FakeApprovalRepo()
    svc.consecutive_repo = FakeApprovalConsecutiveRepo()
    svc.case_repository = FakeCaseRepo(exists_case_codes={"2025-00001", "2025-00002", "2025-00003"})
    svc.case_consecutive_repo = FakeCaseConsecutive()

    # Crear solicitud (caso existe)
    created = await svc.create_approval_request(ApprovalRequestCreate(
        original_case_code="2025-00001",
        complementary_tests=[{"code": "T-101", "name": "Inmuno", "quantity": 2}],
        reason="Necesito más pruebas"
    ))
    print("stage: created", created.approval_code, created.approval_state)
    assert created.approval_code.startswith("AP-")
    assert created.approval_state == ApprovalStateEnum.REQUEST_MADE

    # Intentar duplicado para el mismo caso
    with pytest.raises(ConflictError):
        await svc.create_approval_request(ApprovalRequestCreate(
            original_case_code="2025-00001",
            complementary_tests=[{"code": "T-102", "name": "Molecular", "quantity": 1}],
            reason="Duplicado"
        ))

    # Buscar y contar
    found = await svc.search_approvals(ApprovalRequestSearch(original_case_code="2025-00001"))
    print("stage: searched", len(found))
    assert len(found) == 1
    assert found[0].original_case_code == "2025-00001"
    cnt = await svc.count_approvals(ApprovalRequestSearch(original_case_code="2025-00001"))
    print("stage: counted", cnt)
    assert cnt == 1

    code = created.approval_code
    print("debug keys:", list(svc.repository.by_code.keys()), "code:", code)

    # Gestionar (pending_approval)
    managed = await svc.manage_approval(code)
    if managed is None:
        raise AssertionError("managed is None")
    print("stage: managed", managed.approval_state if managed else None)
    assert managed is not None
    assert managed.approval_state == ApprovalStateEnum.PENDING_APPROVAL

    # Aprobar (crea nuevo caso)
    res = await svc.approve_request(code)
    print("stage: approved", res is not None)
    assert res is not None
    assert res["approval"].approval_state == ApprovalStateEnum.APPROVED
    assert res["new_case"] is not None
    assert "case_code" in res["new_case"]

    # Rechazar no aplica porque ya está aprobado; simular otra solicitud
    created2 = await svc.create_approval_request(ApprovalRequestCreate(
        original_case_code="2025-00002",
        complementary_tests=[{"code": "T-201", "name": "FISH", "quantity": 1}],
        reason="Otra"
    ))
    print("stage: created2", created2.approval_code)
    rej = await svc.reject_request(created2.approval_code)
    print("stage: rejected", rej.approval_state if rej else None)
    assert rej is not None
    assert rej.approval_state == ApprovalStateEnum.REJECTED

    # Actualizar pruebas complementarias en solicitud request_made: primero crear una nueva
    created3 = await svc.create_approval_request(ApprovalRequestCreate(
        original_case_code="2025-00003",
        complementary_tests=[{"code": "T-301", "name": "IHQ", "quantity": 1}],
        reason="Editar"
    ))
    print("stage: created3", created3.approval_code)
    up_tests = await svc.update_complementary_tests(created3.approval_code, [{"code": "T-999", "name": "Nueva", "quantity": 1}])
    print("stage: updated tests", [t.code for t in up_tests.complementary_tests] if up_tests else None)
    assert up_tests is not None
    assert up_tests.complementary_tests[0].code == "T-999"

    # Update general permitido solo en request_made
    upd = await svc.update_approval(created3.approval_code, ApprovalRequestUpdate(approval_state=ApprovalStateEnum.REQUEST_MADE))
    print("stage: updated general", upd.approval_state if upd else None)
    assert upd is not None
    assert upd.approval_state == ApprovalStateEnum.REQUEST_MADE

    # Intento de actualizar en estado distinto debe fallar
    with pytest.raises(BadRequestError):
        await svc.update_approval(code, ApprovalRequestUpdate(approval_state=ApprovalStateEnum.APPROVED))

    # Eliminar
    ok_del = await svc.delete_approval(created3.approval_code)
    print("stage: deleted", ok_del)
    assert ok_del is True

    # Estadísticas
    stats = await svc.get_statistics()
    print("stage: stats", stats.model_dump() if hasattr(stats, 'model_dump') else stats.__dict__)
    assert stats.total_requests >= 2


@pytest.mark.asyncio
async def test_service_create_not_found_case():
    svc = ApprovalService(_DummyDB())
    svc.repository = FakeApprovalRepo()
    svc.consecutive_repo = FakeApprovalConsecutiveRepo()
    svc.case_repository = FakeCaseRepo(exists_case_codes=set())
    svc.case_consecutive_repo = FakeCaseConsecutive()

    with pytest.raises(NotFoundError):
        await svc.create_approval_request(ApprovalRequestCreate(
            original_case_code="NO-CASE",
            complementary_tests=[{"code": "T-1", "name": "X", "quantity": 1}],
            reason="NA"
        ))