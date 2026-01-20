import unittest
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import sync
from app.schemas.sync import SyncPreview, SyncSummary, SyncCommitResult
from app.services.sync_preview_service import SyncPreviewService
from app.services.sync_commit_service import SyncCommitService


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(sync.router, prefix="/api")
    return test_app


def _build_preview() -> SyncPreview:
    now = datetime.now(timezone.utc)
    return SyncPreview(
        session_id=uuid4(),
        created_at=now,
        expires_at=now + timedelta(hours=24),
        offices=[],
        employees=[],
        summary=SyncSummary(),
    )


class SyncPreviewEndpointsTest(unittest.TestCase):
    def setUp(self) -> None:
        async def override_get_db():
            yield None

        self.app = create_test_app()
        self.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()

    def test_preview_creates_session(self) -> None:
        preview = _build_preview()

        async def fake_generate(_self, _db):
            return preview

        with patch.object(SyncPreviewService, "generate_preview", new=fake_generate):
            response = self.client.post("/api/sync/preview")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(UUID(payload["session_id"]), preview.session_id)
        self.assertEqual(payload["summary"]["offices_new"], 0)

    def test_get_session_returns_preview(self) -> None:
        preview = _build_preview()

        async def fake_get(_self, _db, _session_id):
            return preview

        with patch.object(SyncPreviewService, "get_session", new=fake_get):
            response = self.client.get(f"/api/sync/sessions/{preview.session_id}")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(UUID(payload["session_id"]), preview.session_id)

    def test_cancel_session_returns_success(self) -> None:
        preview = _build_preview()

        async def fake_cancel(_self, _db, _session_id):
            return None

        with patch.object(SyncPreviewService, "cancel_session", new=fake_cancel):
            response = self.client.delete(f"/api/sync/sessions/{preview.session_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    def test_update_decision_returns_success(self) -> None:
        preview = _build_preview()

        async def fake_update(_self, _db, _session_id, _data):
            return None

        payload = {
            "record_type": "office",
            "record_id": str(preview.session_id),
            "field_name": "name",
            "decision": "accept",
        }

        with patch.object(SyncCommitService, "update_decision", new=fake_update):
            response = self.client.patch(
                f"/api/sync/sessions/{preview.session_id}/decisions",
                json=payload,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    def test_commit_session_returns_result(self) -> None:
        preview = _build_preview()

        async def fake_commit(_self, _db, _session_id):
            return SyncCommitResult(offices_created=1, employees_updated=2)

        with patch.object(SyncCommitService, "commit_session", new=fake_commit):
            response = self.client.post(f"/api/sync/sessions/{preview.session_id}/commit")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["offices_created"], 1)
        self.assertEqual(payload["employees_updated"], 2)
