# Testing Patterns

**Analysis Date:** 2025-01-20

## Test Framework

**Backend Runner:**
- Python unittest (standard library)
- No pytest configuration detected
- No `requirements-dev.txt` or test dependencies in `requirements.txt`
- Config: None (uses unittest defaults)

**Assertion Library:**
- Python `unittest.TestCase` assertions (`assertEqual`, `assertIn`)

**Run Commands:**
```bash
python -m unittest discover backend/tests  # Run all tests
python -m unittest backend.tests.test_vitec_normalizer_service  # Run specific module
```

**Frontend:**
- No Jest or Vitest configuration detected
- No test files found in `frontend/src/`
- Testing framework: **Not configured**

## Test File Organization

**Location:**
- Backend: Separate `backend/tests/` directory
- Frontend: No test files present

**Naming:**
- Python: `test_*.py` pattern (`test_vitec_normalizer_service.py`, `test_vitec_hub_sync_endpoints.py`)

**Structure:**
```
backend/
└── tests/
    ├── test_vitec_normalizer_service.py    # Unit tests for VitecNormalizerService
    └── test_vitec_hub_sync_endpoints.py    # API endpoint tests
```

## Test Structure

**Suite Organization (Python unittest):**
```python
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import employees, offices
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService


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
        # Arrange
        async def fake_sync(_db):
            return {"total": 3, "synced": 2, ...}

        # Act
        with patch.object(OfficeService, "sync_from_hub", new=fake_sync):
            response = self.client.post("/api/offices/sync")

        # Assert
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 3)
```

**Patterns:**
- `setUp`/`tearDown` for test fixture management
- Type hints on test methods (`: None`)
- FastAPI `TestClient` for API tests
- Dependency overrides for database mocking

**Simple Unit Test Pattern:**
```python
from app.services.vitec_normalizer_service import VitecNormalizerService


def test_normalizer_removes_proaktiv_branding_rules():
    html = """
    <div id="vitecTemplate">
      <style>
        @import url('https://fonts.googleapis.com/...');
        h1 { font-family: Georgia, serif; color: #272630; }
      </style>
      <h1>Title</h1>
    </div>
    """
    normalizer = VitecNormalizerService()
    normalized, report = normalizer.normalize(html)

    assert 'vitec-template="resource:Vitec Stilark"' in normalized
    assert "@import" not in normalized
    assert int(report["removed_css_rules"]) >= 1
```

## Mocking

**Framework:** `unittest.mock` (Python standard library)

**Patterns:**
```python
from unittest.mock import patch

# Patching a service method for API tests
with patch.object(OfficeService, "sync_from_hub", new=fake_sync):
    response = self.client.post("/api/offices/sync")

# Creating async mock functions
async def fake_sync(_db):
    return {
        "total": 3,
        "synced": 2,
        "created": 1,
        "updated": 1,
        "skipped": 1,
    }
```

**What to Mock:**
- Database session (`get_db` dependency override)
- External service calls (`VitecHubService.sync_from_hub`)
- API responses from external systems

**What NOT to Mock:**
- Service business logic (test directly)
- Pydantic validation (let it run)
- HTML parsing (test actual parsing)

## Fixtures and Factories

**Test Data:**
```python
# Inline HTML test fixtures
html = """
<div id="vitecTemplate">
  <style>
    #vitecTemplate table { border-collapse: collapse; width: 100%; }
    .svg-toggle.checkbox { background-image: url("data:image/svg+xml;utf8,abc"); }
  </style>
  <table><tr><td data-label="Test">Cell</td></tr></table>
</div>
"""

# Return value mocks
async def fake_sync(_db):
    return {
        "total": 4,
        "synced": 3,
        "created": 2,
        "updated": 1,
        "skipped": 1,
        "missing_office": 0,
    }
```

**Location:**
- Inline within test functions (no separate fixtures directory)
- Test app factory function (`create_test_app()`)

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
# Not configured - would need pytest-cov or coverage.py
pip install coverage
coverage run -m unittest discover backend/tests
coverage report
```

## Test Types

**Unit Tests:**
- Direct service class testing (`VitecNormalizerService`)
- No database interaction
- Fast execution
- Located in: `backend/tests/test_vitec_normalizer_service.py`

**Integration Tests:**
- FastAPI `TestClient` for API endpoint testing
- Database dependency overridden (mocked)
- Tests router → service interaction
- Located in: `backend/tests/test_vitec_hub_sync_endpoints.py`

**E2E Tests:**
- Framework: **Not configured**
- No Playwright/Cypress/Selenium setup detected

## Common Patterns

**Async Testing:**
```python
# FastAPI TestClient handles async automatically
# For pure async tests, would need pytest-asyncio (not configured)

# Current approach: Mock async with sync TestClient
async def fake_sync(_db):
    return {"total": 3}

with patch.object(OfficeService, "sync_from_hub", new=fake_sync):
    response = self.client.post("/api/offices/sync")  # TestClient handles async
```

**Error Testing:**
```python
# Assert on response status codes
self.assertEqual(response.status_code, 200)

# Assert specific values in response JSON
payload = response.json()
self.assertEqual(payload["total"], 3)
```

**HTML Content Assertions:**
```python
# Check for presence/absence of content in sanitized HTML
assert 'vitec-template="resource:Vitec Stilark"' in normalized
assert "@import" not in normalized
assert "highlight-box" not in normalized
assert int(report["removed_css_rules"]) >= 1
```

## Test Gaps

**Not Tested:**
- Frontend components (no test framework)
- Database models directly (mocked in integration tests)
- Error handling paths
- Authentication/authorization flows
- WebDAV integration
- Azure storage integration

**Priority Areas for Future Tests:**
1. Frontend: Add Vitest + React Testing Library
2. Backend: Add pytest with pytest-asyncio
3. E2E: Add Playwright for critical user flows
4. API: Expand endpoint coverage beyond sync endpoints

## Adding Tests (Recommended Setup)

**Backend (pytest):**
```bash
# Add to requirements.txt
pytest==8.0.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
httpx==0.26.0  # Already present

# Create pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

**Frontend (Vitest):**
```bash
# Install
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom

# vitest.config.ts
import { defineConfig } from 'vitest/config'
export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

---

*Testing analysis: 2025-01-20*
