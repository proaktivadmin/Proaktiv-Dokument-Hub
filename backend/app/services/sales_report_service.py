"""
Sales Report Service

Exports broker revenue (vederlag + andre inntekter) for sold properties
via Vitec Hub API. Matches scope: Proaktiv Eiendomsmegling AS (1120),
statuses 40-48 (sold/completed), Hovedbokskonti for vederlag and andre inntekter.
"""

from __future__ import annotations

import io
import logging
from datetime import datetime

from app.config import settings
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)

# Hovedbokskonti for vederlag (remuneration) - from HOVEDBOKSKONTI UI
VEDERLAG_ACCOUNTS = {
    "3000",
    "3001",
    "3002",
    "3003",
    "3006",
    "3009",
    "3010",
    "3013",
    "3015",
    "3019",
    "3111",
    "3112",
    "3113",
    "3115",
    "3220",
    "3221",
}

# Hovedbokskonti for andre inntekter (other income)
ANDRE_INNTEKTER_ACCOUNTS = {
    "3005",
    "3018",
    "3020",
    "3030",
    "3031",
    "3050",
    "8050",
}

REVENUE_ACCOUNTS = VEDERLAG_ACCOUNTS | ANDRE_INNTEKTER_ACCOUNTS

# Default department: Proaktiv Eiendomsmegling AS
DEFAULT_DEPARTMENT_ID = 1120


def _normalize_account(account: str | None) -> str:
    """Normalize account number for comparison (strip, handle None)."""
    if account is None:
        return ""
    return str(account).strip()


def _is_revenue_account(account: str | None) -> bool:
    """Check if account is vederlag or andre inntekter."""
    return _normalize_account(account) in REVENUE_ACCOUNTS


class SalesReportService:
    """Build sales report from Vitec Hub Accounting API."""

    def __init__(self, hub: VitecHubService | None = None) -> None:
        self._hub = hub or VitecHubService()

    async def build_report(
        self,
        *,
        department_id: int = DEFAULT_DEPARTMENT_ID,
        year: int | None = None,
    ) -> bytes:
        """
        Build Excel sales report for brokers who sold properties this year.

        Args:
            department_id: Vitec department ID (default 1120)
            year: Report year (default: current year)

        Returns:
            Excel file bytes
        """
        if not self._hub.is_configured:
            raise ValueError("Vitec Hub credentials are not configured.")

        installation_id = settings.VITEC_INSTALLATION_ID
        if not installation_id:
            raise ValueError("VITEC_INSTALLATION_ID is not configured.")

        y = year or datetime.now().year
        from_date = f"{y}-01-01T00:00:00"
        to_date = datetime.now().strftime("%Y-%m-%dT23:59:59")
        changed_after = f"{y}-01-01T00:00:00"

        # 1. Fetch employees for broker ID -> name mapping
        employees = await self._hub.get_employees(installation_id)
        broker_map: dict[str, str] = {}
        for emp in employees or []:
            eid = emp.get("employeeId")
            name = emp.get("name")
            if eid and name:
                broker_map[str(eid).strip()] = str(name).strip()

        # 2. Fetch accounting estates (sold/completed) for department
        estates = await self._hub.get_accounting_estates(
            installation_id,
            department_id=department_id,
            changed_after=changed_after,
        )

        # Brokers who have sold: from brokersIdWithRoles on estates with sold date this year
        brokers_with_sales: set[str] = set()
        for est in estates or []:
            sold = est.get("sold")
            if not sold:
                continue
            try:
                sold_dt = datetime.fromisoformat(sold.replace("Z", "+00:00"))
                if sold_dt.year != y:
                    continue
            except (ValueError, TypeError):
                continue
            for b in est.get("brokersIdWithRoles") or []:
                bid = b.get("employeeId")
                if bid:
                    brokers_with_sales.add(str(bid).strip())

        # 3. Fetch all accounting transactions for period and department
        transactions = await self._hub.get_accounting_transactions(
            installation_id,
            from_date=from_date,
            to_date=to_date,
            department_id=department_id,
            ledger_type=1,
        )

        # 4. Filter by revenue accounts and attribute to brokers via userId
        # Transaction userId = broker (4-letter ID). Only count brokers who sold.
        broker_revenue: dict[str, float] = {}
        broker_transaction_count: dict[str, int] = {}
        for txn in transactions or []:
            account = _normalize_account(txn.get("account"))
            if account not in REVENUE_ACCOUNTS:
                continue
            amount = float(txn.get("amount") or 0)
            user_id = str(txn.get("userId") or "").strip()
            if not user_id:
                continue
            if brokers_with_sales and user_id not in brokers_with_sales:
                continue
            broker_revenue[user_id] = broker_revenue.get(user_id, 0) + amount
            broker_transaction_count[user_id] = broker_transaction_count.get(user_id, 0) + 1

        # If no brokers_with_sales from estates, include all brokers with revenue
        if not brokers_with_sales and broker_revenue:
            brokers_with_sales = set(broker_revenue.keys())

        # 5. Build Excel
        return self._build_excel(
            year=y,
            department_id=department_id,
            broker_map=broker_map,
            brokers_with_sales=brokers_with_sales,
            broker_revenue=broker_revenue,
            broker_transaction_count=broker_transaction_count,
        )

    def _build_excel(
        self,
        *,
        year: int,
        department_id: int,
        broker_map: dict[str, str],
        brokers_with_sales: set[str],
        broker_revenue: dict[str, float],
        broker_transaction_count: dict[str, int],
    ) -> bytes:
        """Generate Excel workbook bytes."""
        import openpyxl
        from openpyxl.styles import Font

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Formidlingsrapport"

        # Header
        ws.append(["Formidlingsrapport - Vederlag og andre inntekter"])
        ws.merge_cells("A1:D1")
        ws["A1"].font = Font(bold=True, size=14)
        ws.append([f"Avdeling: {department_id}", f"År: {year}"])
        ws.append([])

        # Column headers
        headers = ["Bruker ID", "Megler", "Antall transaksjoner", "Sum vederlag + andre inntekter (kr)"]
        ws.append(headers)
        for col, _ in enumerate(headers, 1):
            ws.cell(row=4, column=col).font = Font(bold=True)

        # Data rows - only brokers who sold
        brokers_sorted = sorted(brokers_with_sales)
        row = 5
        for broker_id in brokers_sorted:
            name = broker_map.get(broker_id, broker_id)
            revenue = broker_revenue.get(broker_id, 0)
            count = broker_transaction_count.get(broker_id, 0)
            ws.append([broker_id, name, count, round(revenue, 2)])
            row += 1

        # Total row
        total_revenue = sum(broker_revenue.get(b, 0) for b in brokers_with_sales)
        ws.append(
            ["", "Sum", sum(broker_transaction_count.get(b, 0) for b in brokers_with_sales), round(total_revenue, 2)]
        )
        ws.cell(row=row + 1, column=2).font = Font(bold=True)
        ws.cell(row=row + 1, column=4).font = Font(bold=True)

        # Column widths
        ws.column_dimensions["A"].width = 12
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 35

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
