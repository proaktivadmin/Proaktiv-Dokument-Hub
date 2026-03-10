"""Tests for reports API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_sales_report_returns_excel_when_configured(client):
    """GET /api/reports/sales-report returns Excel file when Vitec Hub is configured."""
    fake_excel = b"PK\x03\x04"  # Excel files start with PK (ZIP)

    with patch("app.routers.reports.SalesReportService") as mock_service:
        mock_instance = AsyncMock()
        mock_instance.build_report.return_value = fake_excel
        mock_service.return_value = mock_instance

        with patch("app.services.sales_report_service.settings") as mock_settings:
            mock_settings.VITEC_INSTALLATION_ID = "TEST_INST"
            mock_settings.VITEC_HUB_ACCESS_KEY = "key"
            mock_settings.VITEC_HUB_PRODUCT_LOGIN = "login"
            mock_settings.VITEC_HUB_BASE_URL = "https://hub.test"

            response = client.get("/api/reports/sales-report?department_id=1120")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "formidlingsrapport" in response.headers.get("content-disposition", "").lower()
    assert response.content == fake_excel


def test_sales_report_returns_400_when_not_configured(client):
    """GET /api/reports/sales-report returns 400 when Vitec Hub is not configured."""
    with patch("app.routers.reports.SalesReportService") as mock_service:
        mock_instance = AsyncMock()
        mock_instance.build_report.side_effect = ValueError("VITEC_INSTALLATION_ID is not configured.")
        mock_service.return_value = mock_instance

        response = client.get("/api/reports/sales-report")

    assert response.status_code == 400
    assert "not configured" in response.json().get("detail", "").lower()
