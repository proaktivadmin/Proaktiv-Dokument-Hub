"""
Pytest configuration and shared fixtures.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db


@pytest.fixture
def mock_db():
    """Mock database session that yields None."""

    async def override_get_db():
        yield None

    return override_get_db


@pytest.fixture
def app(mock_db):
    """Create a FastAPI test app with mocked database."""
    from app.routers import sync

    test_app = FastAPI()
    test_app.include_router(sync.router, prefix="/api")
    test_app.dependency_overrides[get_db] = mock_db
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    with TestClient(app) as c:
        yield c
