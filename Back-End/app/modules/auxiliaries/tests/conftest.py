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
        self._items = items
        self._skip = 0
        self._limit = len(items)

    def skip(self, n):
        self._skip = n
        return self

    def limit(self, n):
        self._limit = n
        return self

    async def to_list(self, length):
        return self._items[self._skip:self._skip + min(self._limit, length)]


class FakeCollection:
    def __init__(self):
        self._store = {}
        self._by_email = {}
        self._id_counter = 0

    async def insert_one(self, doc):
        code = doc.get("auxiliar_code")
        email = doc.get("auxiliar_email")
        if code in self._store:
            raise DuplicateKeyError("dup key: auxiliar_code")
        if email in self._by_email:
            raise DuplicateKeyError("dup key: auxiliar_email")
        self._id_counter += 1
        oid = self._id_counter
        saved = dict(doc)
        saved["_id"] = oid
        self._store[code] = saved
        self._by_email[email] = saved
        class R: inserted_id = oid
        return R()

    async def find_one(self, query):
        if "_id" in query:
            for v in self._store.values():
                if v.get("_id") == query["_id"]:
                    return dict(v)
            return None
        if "auxiliar_code" in query:
            return dict(self._store.get(query["auxiliar_code"])) if self._store.get(query["auxiliar_code"]) else None
        if "auxiliar_email" in query:
            for v in self._store.values():
                if v.get("auxiliar_email") == query["auxiliar_email"]:
                    return dict(v)
            return None
        if "auxiliar_code" in query or "auxiliar_email" in query:
            return None
        return None

    def find(self, query):
        items = list(self._store.values())
        def matches(d):
            if not query:
                return True
            for k, v in query.items():
                if k == "$or":
                    ok = False
                    for cond in v:
                        for kk, vv in cond.items():
                            if isinstance(vv, dict) and "$regex" in vv:
                                import re
                                pattern = re.compile(vv["$regex"], re.I if vv.get("$options") == "i" else 0)
                                if pattern.search(d.get(kk, "") or ""):
                                    ok = True
                    if not ok:
                        return False
                elif isinstance(v, dict) and "$regex" in v:
                    import re
                    pattern = re.compile(v["$regex"], re.I if v.get("$options") == "i" else 0)
                    if not pattern.search(d.get(k, "") or ""):
                        return False
                else:
                    if d.get(k) != v:
                        return False
            return True
        filtered = [dict(x) for x in items if matches(x)]
        return FakeCursor(filtered)

    async def update_one(self, filter_q, update_q):
        code = filter_q.get("auxiliar_code")
        doc = self._store.get(code)
        class R: modified_count = 0
        if not doc:
            return R()
        set_data = update_q.get("$set", {})
        doc.update(set_data)
        R.modified_count = 1
        return R()

    async def delete_one(self, filter_q):
        code = filter_q.get("auxiliar_code")
        class R: deleted_count = 0
        doc = self._store.pop(code, None)
        if doc:
            self._by_email.pop(doc.get("auxiliar_email"), None)
            R.deleted_count = 1
        return R()


class MockDB:
    def __init__(self):
        self.auxiliaries = FakeCollection()


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def sample_auxiliar_doc():
    # Campos en inglés, valores en español
    return {
        "auxiliar_code": "AUX-001",
        "auxiliar_name": "Auxiliar de Laboratorio",
        "auxiliar_email": "auxiliar.labo@example.com",
        "is_active": True,
        "observations": "Observación de prueba",
        "password": "secreta123"
    }