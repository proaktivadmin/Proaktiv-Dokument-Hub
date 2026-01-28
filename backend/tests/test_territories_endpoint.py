"""
Tests for territory API endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.routers import territories


@pytest.fixture
def mock_db_session():
    """Fixture to provide a controllable mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def territory_app(mock_db_session):
    test_app = FastAPI()
    test_app.include_router(territories.router, prefix="/api")

    # Mock database dependency
    async def override_get_db():
        yield mock_db_session

    test_app.dependency_overrides[get_db] = override_get_db
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
async def async_client(territory_app):
    transport = ASGITransport(app=territory_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_territory_endpoints(async_client, mock_db_session):
    """Test territory endpoints verify data structure and handling of new sources."""

    # 1. Test Stats
    mock_stats_data = [
        ("vitec_next", 10),
        ("finn", 5),
        ("tjenestetorget", 3),
        ("eiendomsmegler", 2),
        ("meglersmart", 1),
    ]

    # Setup mock_db_session behavior for stats
    mock_db_session.scalar.side_effect = [21, 2, 1]  # total, offices, blacklisted

    mock_result = MagicMock()
    mock_result.all.return_value = mock_stats_data
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/api/territories/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_territories"] == 21
    assert stats["by_source"]["tjenestetorget"] == 3
    assert stats["by_source"]["meglersmart"] == 1

    # 2. Test List
    with patch("app.services.territory_service.OfficeTerritoryService.list", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = ([], 0)
        response = await async_client.get("/api/territories?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    # 3. Test Layers
    with patch(
        "app.services.territory_service.OfficeTerritoryService.get_available_sources", new_callable=AsyncMock
    ) as mock_sources:
        mock_sources.return_value = ["vitec_next", "tjenestetorget"]
        response = await async_client.get("/api/territories/layers")
        assert response.status_code == 200
        layers = response.json()
        assert "tjenestetorget" in layers["layers"]
