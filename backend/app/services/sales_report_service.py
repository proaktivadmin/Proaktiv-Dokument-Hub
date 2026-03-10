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


def _format_date_iso(iso_str: str | None) -> str:
    """Format ISO date to dd.mm.yyyy for display."""
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return str(iso_str)


class SalesReportService:
    """Build sales report from Vitec Hub Accounting API."""

    def __init__(self, hub: VitecHubService | None = None) -> None:
        self._hub = hub or VitecHubService()

    async def build_report(
        self,
        *,
        department_id: int = DEFAULT_DEPARTMENT_ID,
        year: int | None = None,
        include_vat: bool = False,
    ) -> bytes:
        """
        Build Excel sales report for brokers who sold properties this year.

        Args:
            department_id: Vitec department ID (default 1120)
            year: Report year (default: current year)
            include_vat: If True, add vatAmount to revenue sums

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

        # 2. Fetch accounting estates for address mapping
        estates = await self._hub.get_accounting_estates(
            installation_id,
            department_id=department_id,
            changed_after=changed_after,
        )

        estate_address: dict[str, str] = {}
        brokers_with_sales: set[str] = set()
        for est in estates or []:
            eid = str(est.get("estateId") or "").strip()
            addr = str(est.get("address") or "").strip() or "(ukjent adresse)"
            if eid:
                estate_address[eid] = addr
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

        # 3. Fetch all accounting transactions
        transactions = await self._hub.get_accounting_transactions(
            installation_id,
            from_date=from_date,
            to_date=to_date,
            department_id=department_id,
            ledger_type=1,
        )

        # 4. Build broker -> estate -> transactions structure
        # broker_data[broker_id][estate_id] = [txn, txn, ...]
        broker_estates: dict[str, dict[str, list[dict]]] = {}
        for txn in transactions or []:
            account = _normalize_account(txn.get("account"))
            if account not in REVENUE_ACCOUNTS:
                continue
            user_id = str(txn.get("userId") or "").strip()
            if not user_id:
                continue
            if brokers_with_sales and user_id not in brokers_with_sales:
                continue
            estate_id = str(txn.get("estateId") or "").strip() or "(ukjent)"
            if user_id not in broker_estates:
                broker_estates[user_id] = {}
            if estate_id not in broker_estates[user_id]:
                broker_estates[user_id][estate_id] = []
            broker_estates[user_id][estate_id].append(txn)

        if not brokers_with_sales and broker_estates:
            brokers_with_sales = set(broker_estates.keys())

        # 5. Build Excel with expandable detail
        return self._build_excel(
            year=y,
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
            broker_map=broker_map,
            brokers_with_sales=brokers_with_sales,
            broker_estates=broker_estates,
            estate_address=estate_address,
            include_vat=include_vat,
        )

    def _build_excel(
        self,
        *,
        year: int,
        department_id: int,
        from_date: str,
        to_date: str,
        broker_map: dict[str, str],
        brokers_with_sales: set[str],
        broker_estates: dict[str, dict[str, list[dict]]],
        estate_address: dict[str, str],
        include_vat: bool,
    ) -> bytes:
        """Generate Excel workbook with expandable broker/property/transaction detail."""
        import openpyxl
        from openpyxl.styles import Font

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Formidlingsrapport"

        from_display = _format_date_iso(from_date) or from_date[:10]
        to_display = _format_date_iso(to_date) or to_date[:10]
        sum_label = "Sum vederlag + andre inntekter (kr)" + (" inkl. mva" if include_vat else " exkl. mva")

        # Header
        ws.append(["Formidlingsrapport - Vederlag og andre inntekter"])
        ws.merge_cells("A1:C1")
        ws["A1"].font = Font(bold=True, size=14)
        ws.append([f"Avdeling: {department_id}  |  År: {year}  |  Periode: {from_display} - {to_display}"])
        ws.merge_cells("A2:C2")
        ws.append([])

        # Column headers (no Bruker ID)
        headers = ["Megler", "Antall salg", sum_label]
        ws.append(headers)
        header_row = ws.max_row
        for col in range(1, len(headers) + 1):
            ws.cell(row=header_row, column=col).font = Font(bold=True)

        # Data rows with expandable detail
        brokers_sorted = sorted(brokers_with_sales)
        row = header_row + 1

        for broker_id in brokers_sorted:
            name = broker_map.get(broker_id, broker_id)
            estates = broker_estates.get(broker_id, {})
            sale_count = len(estates)

            total = 0.0
            for estate_txns in estates.values():
                for txn in estate_txns:
                    amt = float(txn.get("amount") or 0)
                    if include_vat:
                        amt += float(txn.get("vatAmount") or 0)
                    total += amt

            # Broker summary row (level 0)
            ws.append([name, sale_count, round(total, 2)])
            broker_row = row
            row += 1

            # Property and transaction detail (grouped)
            for estate_id, txns in sorted(estates.items(), key=lambda x: estate_address.get(x[0], x[0])):
                addr = estate_address.get(estate_id, estate_id)
                # Property row (level 1)
                ws.append([f"  {addr}", "", ""])
                ws.cell(row=row, column=1).font = Font(italic=True)
                prop_row = row
                row += 1

                # Transaction rows (level 2)
                for txn in txns:
                    amt = float(txn.get("amount") or 0)
                    if include_vat:
                        amt += float(txn.get("vatAmount") or 0)
                    post_date = _format_date_iso(txn.get("postingDate"))
                    acc = txn.get("account") or ""
                    desc = (txn.get("description") or "")[:40]
                    ws.append([f"    {post_date} | Konto {acc} | {desc}", "", round(amt, 2)])
                    row += 1

                # Group property + its transactions
                ws.row_dimensions.group(prop_row, row - 1, outline_level=2, hidden=False)

            # Group broker + all properties
            if row > broker_row + 1:
                ws.row_dimensions.group(broker_row + 1, row - 1, outline_level=1, hidden=False)

        # Total row
        total_revenue = sum(
            sum(
                float(t.get("amount") or 0) + (float(t.get("vatAmount") or 0) if include_vat else 0)
                for est_txns in broker_estates.get(b, {}).values()
                for t in est_txns
            )
            for b in brokers_with_sales
        )
        total_sales = sum(len(broker_estates.get(b, {})) for b in brokers_with_sales)
        ws.append(["Sum", total_sales, round(total_revenue, 2)])
        total_row = row
        ws.cell(row=total_row, column=1).font = Font(bold=True)
        ws.cell(row=total_row, column=2).font = Font(bold=True)
        ws.cell(row=total_row, column=3).font = Font(bold=True)

        # Column widths
        ws.column_dimensions["A"].width = 45
        ws.column_dimensions["B"].width = 14
        ws.column_dimensions["C"].width = 38

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
