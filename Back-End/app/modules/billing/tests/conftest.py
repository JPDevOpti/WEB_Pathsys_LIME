import os
import sys
import pytest
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

# Asegurar que el paquete `app` sea importable cuando se ejecuta pytest desde la raíz
_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _BASE not in sys.path:
    sys.path.append(_BASE)


class FakeCursor:
    def __init__(self, items):
        self._items = list(items)
        self._skip = 0
        self._limit = len(self._items)

    def skip(self, n):
        self._skip = n
        return self

    def limit(self, n):
        self._limit = n
        return self

    async def to_list(self, length: int):
        return self._items[self._skip:self._skip + min(self._limit, length)]


class FakeCollection:
    def __init__(self):
        self._docs = []
        self._id_seq = 1

    def _match(self, doc, flt):
        for k, v in flt.items():
            if k == "$or":
                if not any(self._match(doc, cond) for cond in v):
                    return False
            elif isinstance(v, dict) and "$regex" in v:
                import re
                if not re.search(v["$regex"], str(doc.get(k, "")), re.I if v.get("$options") == "i" else 0):
                    return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    async def insert_one(self, data: dict):
        # constraints: unique billing_code and billing_email
        for d in self._docs:
            if d.get("billing_code") == data.get("billing_code"):
                raise DuplicateKeyError("duplicate key billing_code")
            if d.get("billing_email") == data.get("billing_email"):
                raise DuplicateKeyError("duplicate key billing_email")
        data = dict(data)
        data.setdefault("_id", str(self._id_seq))
        self._id_seq += 1
        self._docs.append(data)
        class R:
            inserted_id = data["_id"]
        return R()

    async def find_one(self, flt: dict):
        if "_id" in flt:
            for d in self._docs:
                if d.get("_id") == flt["_id"]:
                    return dict(d)
            return None
        for d in self._docs:
            if self._match(d, flt):
                return dict(d)
        return None

    def find(self, flt: dict):
        items = [dict(d) for d in self._docs if self._match(d, flt)]
        return FakeCursor(items)

    async def update_one(self, flt: dict, update: dict):
        modified = 0
        for d in self._docs:
            if self._match(d, flt):
                if "$set" in update:
                    d.update(update["$set"])
                    modified += 1
                break
        class R:
            modified_count = modified
        return R()

    async def delete_one(self, flt: dict):
        deleted = 0
        for i, d in enumerate(list(self._docs)):
            if self._match(d, flt):
                self._docs.pop(i)
                deleted = 1
                break
        class R:
            deleted_count = deleted
        return R()


class MockDB:
    def __init__(self):
        self.billing = FakeCollection()


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def sample_billing_doc():
    # Nombres de campos en inglés, valores en español
    now = datetime.now(timezone.utc)
    return {
        "_id": "507f1f77bcf86cd799439011",
        "billing_code": "FAC-001",
        "billing_name": "Usuario de Facturación",
        "billing_email": "usuario.facturacion@example.com",
        "is_active": True,
        "observations": "Observación inicial",
        "created_at": now,
        "updated_at": now,
    }