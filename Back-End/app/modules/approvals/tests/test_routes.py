import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.modules.approvals.routes.approval_routes import router, get_approval_service
from app.modules.auth.routes.auth_routes import get_current_user_id
from app.modules.approvals.models.approval_request import ApprovalStateEnum


class FakeService:
    def __init__(self):
        self.items = {}
        self.created_order = []
        self.counter = 0

    async def create_approval_request(self, data):
        self.counter += 1
        code = f"AP-TEST-{self.counter:03d}"
        item = {
            "id": f"id-{self.counter}",
            "approval_code": code,
            "original_case_code": data.original_case_code,
            "approval_state": ApprovalStateEnum.REQUEST_MADE,
            "complementary_tests": data.complementary_tests,
            "approval_info": {"reason": data.reason, "request_date": "2025-01-01T00:00:00Z"},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
        }
        self.items[code] = item
        self.created_order.append(code)
        return item

    async def get_approval_by_code(self, code):
        it = self.items.get(code)
        return it

    async def search_approvals(self, search, skip=0, limit=50):
        res = []
        for it in self.items.values():
            ok = True
            if search.original_case_code and search.original_case_code not in it["original_case_code"]:
                ok = False
            if search.approval_state and it["approval_state"] != search.approval_state:
                ok = False
            if ok:
                res.append(it)
        return res[skip: skip + limit]

    async def count_approvals(self, search):
        return len(await self.search_approvals(search))

    async def get_approvals_by_state(self, state, limit=50):
        out = [it for it in self.items.values() if it["approval_state"] == state]
        return out[:limit]

    async def manage_approval(self, code):
        it = self.items.get(code)
        if not it:
            return None
        it["approval_state"] = ApprovalStateEnum.PENDING_APPROVAL
        return it

    async def approve_request(self, code):
        it = self.items.get(code)
        if not it:
            return None
        it["approval_state"] = ApprovalStateEnum.APPROVED
        new_case = {"case_code": "2025-99999"}
        return {"approval": it, "new_case": new_case}

    async def reject_request(self, code):
        it = self.items.get(code)
        if not it:
            return None
        it["approval_state"] = ApprovalStateEnum.REJECTED
        return it

    async def update_approval(self, code, update):
        it = self.items.get(code)
        if not it:
            return None
        # Sólo válido cuando request_made, asumimos en fake que está permitido
        if update.approval_state:
            it["approval_state"] = update.approval_state
        return it

    async def update_complementary_tests(self, code, tests):
        it = self.items.get(code)
        if not it:
            return None
        it["complementary_tests"] = tests
        return it

    async def delete_approval(self, code):
        return self.items.pop(code, None) is not None

    async def get_statistics(self):
        total = len(self.items)
        req = len([1 for it in self.items.values() if it["approval_state"] == ApprovalStateEnum.REQUEST_MADE])
        pen = len([1 for it in self.items.values() if it["approval_state"] == ApprovalStateEnum.PENDING_APPROVAL])
        app = len([1 for it in self.items.values() if it["approval_state"] == ApprovalStateEnum.APPROVED])
        rej = len([1 for it in self.items.values() if it["approval_state"] == ApprovalStateEnum.REJECTED])
        return {
            "total_requests": total,
            "requests_made": req,
            "pending_approval": pen,
            "approved": app,
            "rejected": rej,
        }


def create_app():
    app = FastAPI()
    app.dependency_overrides[get_approval_service] = lambda: fake_service
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.include_router(router, prefix="/approvals")
    return app


fake_service = FakeService()


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_routes_crud_and_search(client):
    # Crear
    payload = {
        "original_case_code": "2025-00001",
        "complementary_tests": [{"code": "T-1", "name": "IHQ", "quantity": 2}],
        "reason": "Se requieren más pruebas"
    }
    r = client.post("/approvals/", json=payload)
    assert r.status_code == 200
    data = r.json()
    code = data["approval_code"]
    assert data["original_case_code"] == "2025-00001"

    # Stats
    rs = client.get("/approvals/stats")
    assert rs.status_code == 200
    stats = rs.json()
    assert stats["total_requests"] >= 1

    # Get by code
    g = client.get(f"/approvals/{code}")
    assert g.status_code == 200
    assert g.json()["approval_code"] == code

    # Search
    sr = client.post("/approvals/search", json={"original_case_code": "2025-000"})
    assert sr.status_code == 200
    body = sr.json()
    assert body["total"] >= 1 and len(body["data"]) >= 1

    # By state
    by_state = client.get("/approvals/state/request_made")
    assert by_state.status_code == 200
    assert isinstance(by_state.json(), list)

    # Manage
    m = client.patch(f"/approvals/{code}/manage")
    assert m.status_code == 200 and m.json()["approval_state"] == "pending_approval"

    # Approve -> data con new_case
    ap = client.patch(f"/approvals/{code}/approve")
    assert ap.status_code == 200
    ap_data = ap.json()
    assert ap_data["success"] is True
    assert ap_data["data"]["new_case"]["case_code"]

    # Reject otra solicitud
    r2 = client.post("/approvals/", json=payload | {"original_case_code": "2025-00002"})
    code2 = r2.json()["approval_code"]
    rej = client.patch(f"/approvals/{code2}/reject")
    assert rej.status_code == 200 and rej.json()["approval_state"] == "rejected"

    # Update PUT
    up = client.put(f"/approvals/{code2}", json={"approval_state": "request_made"})
    assert up.status_code == 200 and up.json()["approval_state"] == "request_made"

    # Update complementary tests
    up2 = client.patch(f"/approvals/{code2}/tests", json={"complementary_tests": [{"code": "T-9", "name": "Nueva", "quantity": 1}]})
    assert up2.status_code == 200 and up2.json()["success"] is True

    # Delete
    dl = client.delete(f"/approvals/{code2}")
    assert dl.status_code == 200 and dl.json()["success"] is True