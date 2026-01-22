"""Tests for sync preview endpoints."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

from app.schemas.sync import SyncCommitResult, SyncPreview, SyncSummary
from app.services.sync_commit_service import SyncCommitService
from app.services.sync_preview_service import SyncPreviewService


def _build_preview() -> SyncPreview:
    """Create a test preview object."""
    now = datetime.now(UTC)
    return SyncPreview(
        session_id=uuid4(),
        created_at=now,
        expires_at=now + timedelta(hours=24),
        offices=[],
        employees=[],
        summary=SyncSummary(),
    )


class TestSyncPreviewEndpoints:
    """Tests for sync preview API endpoints."""

    def test_preview_creates_session(self, client) -> None:
        """POST /api/sync/preview should create a new session."""
        preview = _build_preview()

        async def fake_generate(_self, _db):
            return preview

        with patch.object(SyncPreviewService, "generate_preview", new=fake_generate):
            response = client.post("/api/sync/preview")

        assert response.status_code == 200
        payload = response.json()
        assert UUID(payload["session_id"]) == preview.session_id
        assert payload["summary"]["offices_new"] == 0

    def test_get_session_returns_preview(self, client) -> None:
        """GET /api/sync/sessions/{id} should return the preview."""
        preview = _build_preview()

        async def fake_get(_self, _db, _session_id):
            return preview

        with patch.object(SyncPreviewService, "get_session", new=fake_get):
            response = client.get(f"/api/sync/sessions/{preview.session_id}")

        assert response.status_code == 200
        payload = response.json()
        assert UUID(payload["session_id"]) == preview.session_id

    def test_cancel_session_returns_success(self, client) -> None:
        """DELETE /api/sync/sessions/{id} should cancel the session."""
        preview = _build_preview()

        async def fake_cancel(_self, _db, _session_id):
            return None

        with patch.object(SyncPreviewService, "cancel_session", new=fake_cancel):
            response = client.delete(f"/api/sync/sessions/{preview.session_id}")

        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_update_decision_returns_success(self, client) -> None:
        """PATCH /api/sync/sessions/{id}/decisions should update a decision."""
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
            response = client.patch(
                f"/api/sync/sessions/{preview.session_id}/decisions",
                json=payload,
            )

        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_commit_session_returns_result(self, client) -> None:
        """POST /api/sync/sessions/{id}/commit should commit the session."""
        preview = _build_preview()

        async def fake_commit(_self, _db, _session_id):
            return SyncCommitResult(offices_created=1, employees_updated=2)

        with patch.object(SyncCommitService, "commit_session", new=fake_commit):
            response = client.post(f"/api/sync/sessions/{preview.session_id}/commit")

        assert response.status_code == 200
        payload = response.json()
        assert payload["offices_created"] == 1
        assert payload["employees_updated"] == 2
