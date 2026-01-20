import unittest
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import sync
from app.schemas.sync import SyncPreview, SyncSummary
from app.services.sync_preview_service import SyncPreviewService


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
