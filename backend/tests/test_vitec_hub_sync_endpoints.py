import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import employees, offices
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(offices.router, prefix="/api")
    test_app.include_router(employees.router, prefix="/api")
    return test_app


class VitecHubSyncEndpointsTest(unittest.TestCase):
    def setUp(self) -> None:
        async def override_get_db():
            yield None

        self.app = create_test_app()
        self.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()

    def test_sync_offices_returns_counts(self) -> None:
        async def fake_sync(_db):
            return {
                "total": 3,
                "synced": 2,
                "created": 1,
                "updated": 1,
                "skipped": 1,
            }

        with patch.object(OfficeService, "sync_from_hub", new=fake_sync):
            response = self.client.post("/api/offices/sync")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 3)
        self.assertEqual(payload["synced"], 2)
        self.assertEqual(payload["created"], 1)
        self.assertEqual(payload["updated"], 1)
        self.assertEqual(payload["skipped"], 1)

    def test_sync_employees_returns_counts(self) -> None:
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
            response = self.client.post("/api/employees/sync")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 4)
        self.assertEqual(payload["synced"], 3)
        self.assertEqual(payload["created"], 2)
        self.assertEqual(payload["updated"], 1)
        self.assertEqual(payload["skipped"], 1)
        self.assertEqual(payload["missing_office"], 0)
