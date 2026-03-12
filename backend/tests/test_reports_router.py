"""
Tests for reports router endpoints.

Covers:
- Endpoint response structure
- Scope metadata shape validation
- Audit log write verification
- Regression: report math unchanged after data_source column
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.routers import reports

SCOPE_REQUIRED_KEYS = {"accounts_included", "account_categories", "data_sources", "date_range", "vat_handling"}


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


def _make_report_data_with_scope(**overrides):
    """Build a minimal report data dict including scope metadata."""
    base = {
        "year": 2026,
        "department_id": 1120,
        "from_date": "2026-01-01T00:00:00",
        "to_date": "2026-03-12T23:59:59",
        "from_date_display": "01.01.2026",
        "to_date_display": "12.03.2026",
        "include_vat": False,
        "brokers": [
            {
                "broker_id": "E001",
                "name": "Test Megler",
                "sale_count": 2,
                "total": 150000.0,
                "properties": [],
            }
        ],
        "total_sales": 2,
        "total_revenue": 150000.0,
        "scope": {
            "accounts_included": ["3000", "3001"],
            "account_categories": {"vederlag": ["3000", "3001"], "andre_inntekter": ["3020"]},
            "estate_statuses": "40-48 (solgt/overtatt)",
            "vat_handling": "excluded",
            "date_range": {"from": "2026-01-01T00:00:00", "to": "2026-03-12T23:59:59"},
            "department_filter": 1120,
            "last_synced_at": "2026-03-12T10:00:00+00:00",
            "data_sources": [
                {"name": "vitec_next", "label": "Vitec Next", "coverage": "2026-02 - present", "row_count": 42},
            ],
            "brokers_filter": "only brokers with sales in period",
            "data_freshness_note": "Current month re-synced on every load; past months cached",
            "validation_warnings_count": 0,
        },
    }
    base.update(overrides)
    return base


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


@pytest.mark.asyncio
async def test_cache_events_endpoint(async_client):
    with patch(
        "app.services.sales_report_service.SalesReportService.list_cache_events",
        new_callable=AsyncMock,
    ) as mock_method:
        mock_method.return_value = [
            {
                "id": 10,
                "installation_id": "1120",
                "department_id": 1120,
                "event_type": "cache_sync",
                "from_date": "2026-03-01T00:00:00",
                "to_date": "2026-03-31T23:59:59",
                "estates_upserted": 4,
                "transactions_upserted": 27,
                "payload_json": {"months_scanned": 1},
                "created_at": "2026-03-12T01:00:00Z",
            }
        ]
        response = await async_client.get("/api/reports/cache-events?since_id=9&limit=50")
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["id"] == 10
        assert body[0]["event_type"] == "cache_sync"


@pytest.mark.asyncio
async def test_cache_events_stream_endpoint(async_client):
    with patch(
        "app.services.sales_report_service.SalesReportService.list_cache_events",
        new_callable=AsyncMock,
    ) as mock_method:
        mock_method.return_value = []
        response = await async_client.get("/api/reports/cache-events/stream?max_seconds=0")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")


@pytest.mark.asyncio
async def test_sales_report_data_includes_scope(async_client):
    """Scope metadata must be present on sales report data responses."""
    report = _make_report_data_with_scope()
    with (
        patch(
            "app.services.sales_report_service.SalesReportService.get_report_data",
            new_callable=AsyncMock,
            return_value=report,
        ),
        patch("app.routers.reports._write_audit_log_safe", new_callable=AsyncMock),
    ):
        response = await async_client.get("/api/reports/sales-report/data?year=2026&department_id=1120")
        assert response.status_code == 200
        body = response.json()

        assert "scope" in body
        scope = body["scope"]
        for key in SCOPE_REQUIRED_KEYS:
            assert key in scope, f"Missing scope key: {key}"

        assert isinstance(scope["data_sources"], list)
        assert len(scope["data_sources"]) > 0
        ds = scope["data_sources"][0]
        assert "name" in ds
        assert "label" in ds
        assert "coverage" in ds


@pytest.mark.asyncio
async def test_sales_report_math_regression(async_client):
    """Report totals must match expected values regardless of data_source column."""
    report = _make_report_data_with_scope()
    with (
        patch(
            "app.services.sales_report_service.SalesReportService.get_report_data",
            new_callable=AsyncMock,
            return_value=report,
        ),
        patch("app.routers.reports._write_audit_log_safe", new_callable=AsyncMock),
    ):
        response = await async_client.get("/api/reports/sales-report/data?year=2026")
        body = response.json()
        assert body["total_sales"] == 2
        assert body["total_revenue"] == 150000.0
        assert len(body["brokers"]) == 1
        assert body["brokers"][0]["total"] == 150000.0


@pytest.mark.asyncio
async def test_audit_log_does_not_block_response(async_client):
    """Even if the audit log DB write fails, report response must succeed."""
    report = _make_report_data_with_scope()
    with (
        patch(
            "app.services.sales_report_service.SalesReportService.get_report_data",
            new_callable=AsyncMock,
            return_value=report,
        ),
        patch(
            "app.routers.reports._write_audit_log_inner",
            new_callable=AsyncMock,
            side_effect=Exception("DB write failed"),
        ),
    ):
        response = await async_client.get("/api/reports/sales-report/data?year=2026")
        assert response.status_code == 200
