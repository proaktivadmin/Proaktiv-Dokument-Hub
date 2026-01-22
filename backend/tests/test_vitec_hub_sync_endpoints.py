"""Tests for Vitec Hub sync endpoints."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import employees, offices
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService


@pytest.fixture
def vitec_app():
    """Create a FastAPI test app with office and employee routers."""

    async def override_get_db():
        yield None

    test_app = FastAPI()
    test_app.include_router(offices.router, prefix="/api")
    test_app.include_router(employees.router, prefix="/api")
    test_app.dependency_overrides[get_db] = override_get_db
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
def vitec_client(vitec_app):
    """Create a test client for the vitec app."""
    with TestClient(vitec_app) as c:
        yield c


class TestVitecHubSyncEndpoints:
    """Tests for Vitec Hub sync API endpoints."""

    def test_sync_offices_returns_counts(self, vitec_client) -> None:
        """POST /api/offices/sync should return sync counts."""

        async def fake_sync(_db):
            return {
                "total": 3,
                "synced": 2,
                "created": 1,
                "updated": 1,
                "skipped": 1,
            }

        with patch.object(OfficeService, "sync_from_hub", new=fake_sync):
            response = vitec_client.post("/api/offices/sync")

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 3
        assert payload["synced"] == 2
        assert payload["created"] == 1
        assert payload["updated"] == 1
        assert payload["skipped"] == 1

    def test_sync_employees_returns_counts(self, vitec_client) -> None:
        """POST /api/employees/sync should return sync counts."""

        async def fake_sync(_db):
            return {
                "total": 4,
                "synced": 3,
                "created": 2,
                "updated": 1,
                "skipped": 1,
                "missing_office": 0,
            }

        with patch.object(EmployeeService, "sync_from_hub", new=fake_sync):
            response = vitec_client.post("/api/employees/sync")

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 4
        assert payload["synced"] == 3
        assert payload["created"] == 2
        assert payload["updated"] == 1
        assert payload["skipped"] == 1
        assert payload["missing_office"] == 0
