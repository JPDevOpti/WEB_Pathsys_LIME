import os
import sys
import types
import asyncio
import pytest
from datetime import datetime, timezone


# Asegurar que el paquete 'app' sea importable en pytest
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    def skip(self, *_):
        return self

    def limit(self, *_):
        return self

    def sort(self, *_):
        return self

    async def to_list(self, length):
        return self._docs[:length]


class FakeCollection:
    def __init__(self):
        self._docs = []

    # Helpers
    def _match(self, doc, query):
        if not query:
            return True
        for k, v in query.items():
            # Soporta nested paths con un solo nivel, ej: "approval_info.request_date"
            if "." in k:
                first, rest = k.split(".", 1)
                sub = doc.get(first, {})
                # Rango de fechas
                if isinstance(v, dict) and ("$gte" in v or "$lte" in v):
                    val = sub.get(rest)
                    if "$gte" in v and (val is None or val < v["$gte"]):
                        return False
                    if "$lte" in v and (val is None or val > v["$lte"]):
                        return False
                else:
                    if sub.get(rest) != v:
                        return False
            else:
                if isinstance(v, dict) and "$regex" in v:
                    import re
                    patt = re.compile(v["$regex"], re.I if v.get("$options") == "i" else 0)
                    if not patt.search(str(doc.get(k, ""))):
                        return False
                else:
                    if doc.get(k) != v:
                        return False
        return True

    async def insert_one(self, doc):
        # Simular _id
        if "_id" not in doc:
            from bson import ObjectId
            doc["_id"] = ObjectId()
        # timestamps
        doc.setdefault("created_at", datetime.now(timezone.utc))
        doc.setdefault("updated_at", datetime.now(timezone.utc))
        self._docs.append(doc)

        class R:
            def __init__(self, _id):
                self.inserted_id = _id
        return R(doc["_id"])

    async def find_one(self, query):
        for d in self._docs:
            if self._match(d, query):
                return d
        return None

    def find(self, query):
        results = [d for d in self._docs if self._match(d, query)]
        return FakeCursor(results)

    async def count_documents(self, query):
        return len([d for d in self._docs if self._match(d, query)])

    async def update_one(self, query, update):
        modified = 0
        for d in self._docs:
            if self._match(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                modified += 1
                break

        class R:
            def __init__(self, mc):
                self.modified_count = mc
        return R(modified)

    async def find_one_and_update(self, query, update, return_document=True):
        for d in self._docs:
            if self._match(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                return d
        return None

    async def delete_one(self, query):
        before = len(self._docs)
        self._docs = [d for d in self._docs if not self._match(d, query)]

        class R:
            def __init__(self, dc):
                self.deleted_count = dc
        return R(before - len(self._docs))

    def aggregate(self, pipeline):
        # Soporta pipeline simple de agrupación por approval_state
        if pipeline and "$group" in pipeline[0]:
            field = pipeline[0]["$group"]["_id"].lstrip("$")
            counts = {}
            for d in self._docs:
                key = d.get(field)
                counts[key] = counts.get(key, 0) + 1
            out = [{"_id": k, "count": v} for k, v in counts.items()]
            return FakeCursor(out)
        return FakeCursor([])

    async def create_index(self, *_args, **_kwargs):
        return "ok"


class MockDB:
    def __init__(self):
        self.approval_requests = FakeCollection()
        self.cases = FakeCollection()

    def __getitem__(self, name: str):
        return getattr(self, name)


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def sample_approval_doc():
    return {
        "approval_code": "AP-2025-001",
        "original_case_code": "2025-00001",
        "approval_state": "request_made",
        "complementary_tests": [
            {"code": "T-101", "name": "Prueba Especial", "quantity": 2}
        ],
        "approval_info": {
            "reason": "Pruebas adicionales necesarias",
            "request_date": datetime.now(timezone.utc)
        },
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }