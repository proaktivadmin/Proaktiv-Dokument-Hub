"""
Tests for Entra office import endpoint.
"""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import entra_sync
from app.schemas.entra_sync import EntraOfficeImportResult
from app.services.entra_sync_service import EntraSyncService


def _build_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(entra_sync.router, prefix="/api")
    return test_app


@pytest.fixture
def client():
    app = _build_app()
    with TestClient(app) as test_client:
        yield test_client


def test_import_offices_uses_defaults(client) -> None:
    result = EntraOfficeImportResult(
        success=True,
        dry_run=True,
        offices_loaded=3,
        matched_updated=2,
        offices_not_matched=1,
        groups_not_matched=0,
        error=None,
    )

    with patch.object(EntraSyncService, "import_entra_offices", return_value=result) as mock_import:
        response = client.post("/api/entra-sync/import-offices", json={"dry_run": True})

    assert response.status_code == 200
    mock_import.assert_called_once_with(
        dry_run=True,
        filter_office_id=None,
        fetch_details=False,
    )
    payload = response.json()
    assert payload["success"] is True
    assert payload["dry_run"] is True
    assert payload["offices_loaded"] == 3


def test_import_offices_passes_filter_and_details(client) -> None:
    office_id = uuid4()
    result = EntraOfficeImportResult(
        success=True,
        dry_run=False,
        offices_loaded=1,
        matched_updated=1,
        offices_not_matched=0,
        groups_not_matched=0,
        error=None,
    )

    with patch.object(EntraSyncService, "import_entra_offices", return_value=result) as mock_import:
        response = client.post(
            "/api/entra-sync/import-offices",
            json={"filter_office_id": str(office_id), "fetch_details": True},
        )

    assert response.status_code == 200
    mock_import.assert_called_once_with(
        dry_run=False,
        filter_office_id=str(office_id),
        fetch_details=True,
    )
    payload = response.json()
    assert payload["matched_updated"] == 1
