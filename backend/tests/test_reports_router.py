"""
Tests for reports router endpoints.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.routers import reports


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def reports_app(mock_db_session):
    app = FastAPI()
    app.include_router(reports.router, prefix="/api")

    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(reports_app):
    transport = ASGITransport(app=reports_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_franchise_report_endpoint(async_client):
    with patch(
        "app.services.sales_report_service.SalesReportService.get_franchise_report_data",
        new_callable=AsyncMock,
    ) as mock_method:
        mock_method.return_value = {
            "year": 2026,
            "departments": [],
            "summary": {"total_sales": 0, "total_revenue": 0.0, "department_count": 0},
        }
        response = await async_client.get("/api/reports/sales-report/franchise?year=2026")
        assert response.status_code == 200
        assert response.json()["summary"]["department_count"] == 0


@pytest.mark.asyncio
async def test_best_performers_endpoint(async_client):
    with patch(
        "app.services.sales_report_service.SalesReportService.get_best_performers_data",
        new_callable=AsyncMock,
    ) as mock_method:
        mock_method.return_value = {
            "from_date": "2026-03-10",
            "to_date": "2026-03-16",
            "eiendomsmegler": [],
            "eiendomsmeglerfullmektig": [],
            "unknown": [],
            "departments": [],
            "top_n": 5,
            "include_vat": False,
        }
        response = await async_client.get("/api/reports/best-performers?top_n=5")
        assert response.status_code == 200
        assert response.json()["top_n"] == 5


@pytest.mark.asyncio
async def test_budget_comparison_endpoint(async_client):
    with patch(
        "app.services.report_budget_service.ReportBudgetService.comparison",
        new_callable=AsyncMock,
    ) as mock_method:
        mock_method.return_value = {
            "department_id": 1120,
            "year": 2026,
            "include_vat": False,
            "months": [],
            "ytd_actual": 0.0,
            "ytd_budget": 0.0,
            "ytd_variance": 0.0,
            "ytd_achieved_percent": 0.0,
            "projected_year_end": 0.0,
            "status": "On track",
        }
        response = await async_client.get("/api/reports/budgets/comparison?department_id=1120&year=2026")
        assert response.status_code == 200
        assert response.json()["status"] == "On track"


@pytest.mark.asyncio
async def test_create_subscription_endpoint(async_client):
    payload = {
        "name": "Weekly performers",
        "report_type": "best_performers",
        "cadence": "weekly",
        "recipients": ["ceo@example.com"],
        "department_ids": [1120],
        "include_vat": False,
        "day_of_week": 5,
        "day_of_month": 1,
        "send_hour": 8,
        "timezone": "Europe/Oslo",
        "is_active": True,
    }
    with patch(
        "app.services.report_subscription_service.ReportSubscriptionService.create",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = {
            "id": "11111111-1111-1111-1111-111111111111",
            **payload,
            "last_run_at": None,
            "next_run_at": None,
            "last_status": None,
            "last_error": None,
            "created_at": "2026-03-11T00:00:00Z",
            "updated_at": "2026-03-11T00:00:00Z",
        }
        response = await async_client.post("/api/reports/subscriptions", json=payload)
        assert response.status_code == 200
        assert response.json()["name"] == payload["name"]
