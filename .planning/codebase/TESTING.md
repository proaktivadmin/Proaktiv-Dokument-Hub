# Testing Patterns

**Analysis Date:** 2026-01-22

## Test Framework

**Backend Runner:**
- Pytest 8.0.0+ with pytest-asyncio 0.23.0+
- Configuration: `backend/pytest.ini`
- Dev dependencies: `backend/requirements-dev.txt`

**Backend Assertion Library:**
- Pytest native assertions (`assert`)
- Pytest markers (`@pytest.mark.xfail`, `@pytest.mark.asyncio`)

**Backend Run Commands:**
```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_vitec_normalizer_service.py  # Run specific file
pytest --cov=app          # With coverage
```

**Frontend Runner:**
- Vitest 4.0.17 with jsdom environment
- Configuration: `frontend/vitest.config.ts`
- Setup file: `frontend/vitest.setup.tsx`

**Frontend Assertion Library:**
- Vitest native (`expect`, `vi.mock`, `vi.fn`)
- @testing-library/jest-dom matchers

**Frontend Run Commands:**
```bash
cd frontend
npm run test              # Watch mode
npm run test:run          # Single run
npm run test:coverage     # With coverage
```

## Test File Organization

**Location:**
- Backend: Separate `backend/tests/` directory
- Frontend: `frontend/src/__tests__/` directory

**Naming:**
- Python: `test_*.py` pattern
- TypeScript: `*.test.ts` or `*.test.tsx` pattern

**Structure:**
```
backend/
└── tests/
    ├── conftest.py                         # Pytest fixtures
    ├── test_sync_preview_endpoints.py      # Sync preview API tests
    ├── test_vitec_hub_sync_endpoints.py    # Vitec Hub API tests
    └── test_vitec_normalizer_service.py    # Normalizer unit tests

frontend/
├── vitest.config.ts                        # Vitest configuration
├── vitest.setup.tsx                        # Test setup (mocks)
└── src/
    └── __tests__/
        └── utils.test.ts                   # Utility function tests
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

## CI Integration

**GitHub Actions runs all tests on:**
- Push to `main`
- Pull requests to `main`

**Backend CI:**
```yaml
- name: Run pytest
  run: pytest
  env:
    PYTHONPATH: ${{ github.workspace }}/backend
```

**Frontend CI:**
```yaml
- name: Run Vitest
  run: npm run test:run
```

## Test Gaps

**Not Tested:**
- Database models directly (mocked in integration tests)
- Error handling paths
- Authentication/authorization flows
- WebDAV integration
- Azure storage integration

**Priority Areas for Future Tests:**
1. E2E: Add Playwright for critical user flows
2. API: Expand endpoint coverage
3. Frontend: Add React component tests with Testing Library

## Current Test Status

**Backend Tests:** 10 tests
- 7 passing
- 3 xfail (normalizer CSS features not yet implemented)

**Frontend Tests:** 4 tests
- 4 passing (utility functions)

---

*Testing analysis: 2026-01-22*
