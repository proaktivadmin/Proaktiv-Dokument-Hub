"""
Sales Report Service

Exports broker revenue (vederlag + andre inntekter) for sold properties
via Vitec Hub API. Matches scope: Proaktiv Eiendomsmegling AS (1120),
statuses 40-48 (sold/completed), Hovedbokskonti for vederlag and andre inntekter.
"""

from __future__ import annotations

import asyncio
import io
import logging
import re
from collections import defaultdict
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


def _build_estate_address(est: dict) -> str:
    """Build display address from estate object (Vitec may use address, streetAddress, etc.)."""
    addr = str(est.get("address") or "").strip()
    if addr:
        return addr
    street = str(est.get("streetAddress") or est.get("street_address") or "").strip()
    postal = str(est.get("postalCode") or est.get("zipCode") or est.get("postal_code") or "").strip()
    city = str(est.get("city") or est.get("visitCity") or "").strip()
    parts = [p for p in [street, f"{postal} {city}".strip()] if p]
    return ", ".join(parts) if parts else ""


def _revenue_amount(amount: float, vat_amount: float, include_vat: bool) -> float:
    """Revenue as positive number (API may return negative for credits)."""
    total = float(amount) + (float(vat_amount) if include_vat else 0)
    return abs(total)


def _extract_display_value(obj: object) -> str:
    """Extract display string from API value (string, or dict with name/key)."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, dict):
        return str(obj.get("name") or obj.get("key") or obj.get("value") or obj.get("displayName") or "").strip()
    return str(obj).strip()


def _build_estate_metadata(est: dict) -> dict[str, str]:
    """Extract property type and assignment type from estate (Vitec field names may vary)."""
    prop_type = _extract_display_value(
        est.get("propertyType")
        or est.get("property_type")
        or est.get("estateType")
        or est.get("estate_type")
        or est.get("boligtype")
        or est.get("grunntype")
    )
    assign_type = _extract_display_value(
        est.get("assignmentType") or est.get("assignment_type") or est.get("oppdragstype")
    )
    return {"property_type": prop_type or "—", "assignment_type": assign_type or "—"}


def _infer_broker_role(employee: dict) -> str:
    """Infer performer category from employee fields."""
    role_blob = " ".join(
        [
            str(employee.get("title") or ""),
            str(employee.get("jobTitle") or ""),
            str(employee.get("employeeType") or ""),
            str(employee.get("role") or ""),
        ]
    ).lower()
    if "fullmektig" in role_blob:
        return "eiendomsmeglerfullmektig"
    if "eiendomsmegler" in role_blob or re.search(r"\bmegler\b", role_blob):
        return "eiendomsmegler"
    return "unknown"


class SalesReportService:
    """Build sales report from Vitec Hub Accounting API."""

    def __init__(self, hub: VitecHubService | None = None) -> None:
        self._hub = hub or VitecHubService()

    async def build_report(
        self,
        *,
        department_id: int = DEFAULT_DEPARTMENT_ID,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
    ) -> bytes:
        """
        Build Excel sales report for brokers who sold properties this year.
        """
        result = await self._fetch_report_data(
            department_id=department_id,
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
        )
        report_data, broker_map, brokers_with_sales, broker_estates, estate_address, estate_metadata, _ = result
        y = report_data["year"]
        from_date = report_data["from_date"]
        to_date = report_data["to_date"]

        return self._build_excel(
            year=y,
            department_id=department_id,
            from_date=from_date,
            to_date=to_date,
            broker_map=broker_map,
            brokers_with_sales=brokers_with_sales,
            broker_estates=broker_estates,
            estate_address=estate_address,
            estate_metadata=estate_metadata,
            include_vat=include_vat,
        )

    async def get_report_data(
        self,
        *,
        department_id: int = DEFAULT_DEPARTMENT_ID,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
    ) -> dict:
        """
        Fetch and return sales report data as structured dict for JSON API.
        """
        result = await self._fetch_report_data(
            department_id=department_id,
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
        )
        return result[0]

    async def get_franchise_report_data(
        self,
        *,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
        department_ids: list[int] | None = None,
    ) -> dict:
        """
        Fetch franchise report data across departments.
        """
        installation_id = settings.VITEC_INSTALLATION_ID
        if not installation_id:
            raise ValueError("VITEC_INSTALLATION_ID is not configured.")

        if department_ids:
            selected_departments = list(dict.fromkeys(department_ids))
        else:
            departments_raw = await self._hub.get_departments(installation_id)
            selected_departments = []
            for dep in departments_raw or []:
                dep_id = dep.get("departmentId") or dep.get("id")
                dep_name = str(dep.get("name") or "").lower()
                if dep_id is None:
                    continue
                if "oppgjør" in dep_name or "pacta" in dep_name:
                    continue
                try:
                    selected_departments.append(int(dep_id))
                except (TypeError, ValueError):
                    continue

        selected_departments = list(dict.fromkeys(selected_departments))
        if not selected_departments:
            return {
                "year": year or datetime.now().year,
                "from_date": from_date,
                "to_date": to_date,
                "include_vat": include_vat,
                "departments": [],
                "summary": {
                    "total_sales": 0,
                    "total_revenue": 0.0,
                    "department_count": 0,
                },
            }

        tasks = [
            self.get_report_data(
                department_id=dep_id,
                year=year,
                from_date=from_date,
                to_date=to_date,
                include_vat=include_vat,
            )
            for dep_id in selected_departments
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        departments: list[dict] = []
        total_sales = 0
        total_revenue = 0.0

        for dep_id, result in zip(selected_departments, results, strict=False):
            if isinstance(result, Exception):
                logger.warning("Skipping franchise department %s: %s", dep_id, result)
                continue
            dep_revenue = float(result.get("total_revenue") or 0.0)
            dep_sales = int(result.get("total_sales") or 0)
            total_sales += dep_sales
            total_revenue += dep_revenue
            departments.append(
                {
                    "department_id": dep_id,
                    "department_name": f"Avdeling {dep_id}",
                    "total_sales": dep_sales,
                    "total_revenue": round(dep_revenue, 2),
                    "brokers": result.get("brokers", []),
                }
            )

        for dep in departments:
            dep_total = float(dep["total_revenue"])
            dep["revenue_share_percent"] = round((dep_total / total_revenue * 100.0), 2) if total_revenue > 0 else 0.0

        departments.sort(key=lambda d: d["total_revenue"], reverse=True)
        first = departments[0] if departments else {}
        return {
            "year": first.get("year", year or datetime.now().year),
            "from_date": first.get("from_date", from_date),
            "to_date": first.get("to_date", to_date),
            "from_date_display": first.get("from_date_display"),
            "to_date_display": first.get("to_date_display"),
            "include_vat": include_vat,
            "departments": departments,
            "summary": {
                "total_sales": total_sales,
                "total_revenue": round(total_revenue, 2),
                "department_count": len(departments),
            },
        }

    async def get_best_performers_data(
        self,
        *,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
        department_ids: list[int] | None = None,
        top_n: int = 5,
    ) -> dict:
        """
        Build best-performers leaderboard by role and department.
        """
        franchise = await self.get_franchise_report_data(
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
            department_ids=department_ids,
        )

        installation_id = settings.VITEC_INSTALLATION_ID
        employees = await self._hub.get_employees(installation_id) if installation_id else []
        role_by_broker: dict[str, str] = {}
        for emp in employees or []:
            eid = str(emp.get("employeeId") or "").strip()
            if not eid:
                continue
            role_by_broker[eid] = _infer_broker_role(emp)

        brokers_agg: dict[str, dict] = defaultdict(
            lambda: {"broker_id": "", "name": "", "role": "unknown", "total_revenue": 0.0, "total_sales": 0}
        )
        for dep in franchise.get("departments", []):
            for broker in dep.get("brokers", []):
                bid = str(broker.get("broker_id") or "").strip()
                if not bid:
                    continue
                row = brokers_agg[bid]
                row["broker_id"] = bid
                row["name"] = broker.get("name") or bid
                row["role"] = role_by_broker.get(bid, "unknown")
                row["total_revenue"] += float(broker.get("total") or 0.0)
                row["total_sales"] += int(broker.get("sale_count") or 0)

        def _sort_rows(rows: list[dict]) -> list[dict]:
            return sorted(rows, key=lambda r: (-float(r["total_revenue"]), str(r["name"]).lower()))

        rows = [r | {"total_revenue": round(float(r["total_revenue"]), 2)} for r in brokers_agg.values()]
        eiendomsmegler = _sort_rows([r for r in rows if r["role"] == "eiendomsmegler"])[:top_n]
        fullmektig = _sort_rows([r for r in rows if r["role"] == "eiendomsmeglerfullmektig"])[:top_n]
        unknown = _sort_rows([r for r in rows if r["role"] == "unknown"])[:top_n]
        departments = [
            {
                "department_id": d["department_id"],
                "department_name": d["department_name"],
                "total_revenue": d["total_revenue"],
                "total_sales": d["total_sales"],
            }
            for d in sorted(
                franchise.get("departments", []),
                key=lambda d: (-float(d.get("total_revenue") or 0.0), str(d.get("department_name", ""))),
            )[:top_n]
        ]

        return {
            "from_date": franchise.get("from_date"),
            "to_date": franchise.get("to_date"),
            "from_date_display": franchise.get("from_date_display"),
            "to_date_display": franchise.get("to_date_display"),
            "include_vat": include_vat,
            "top_n": top_n,
            "eiendomsmegler": eiendomsmegler,
            "eiendomsmeglerfullmektig": fullmektig,
            "unknown": unknown,
            "departments": departments,
        }

    async def build_best_performers_report(
        self,
        *,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
        department_ids: list[int] | None = None,
        top_n: int = 5,
    ) -> bytes:
        """
        Generate Excel workbook for best performers leaderboard.
        """
        import openpyxl
        from openpyxl.styles import Font

        data = await self.get_best_performers_data(
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
            department_ids=department_ids,
            top_n=top_n,
        )
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Best performers"
        ws.append(["Best performers"])
        ws["A1"].font = Font(bold=True, size=14)
        ws.append([f"Periode: {data.get('from_date_display', '')} - {data.get('to_date_display', '')}"])
        ws.append([])

        def add_section(title: str, rows: list[dict], name_key: str = "name") -> None:
            ws.append([title])
            ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
            ws.append(["Navn", "Antall salg", "Omsetning (kr)"])
            ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
            ws.cell(row=ws.max_row, column=2).font = Font(bold=True)
            ws.cell(row=ws.max_row, column=3).font = Font(bold=True)
            for row in rows:
                ws.append(
                    [row.get(name_key, "—"), int(row.get("total_sales", 0)), float(row.get("total_revenue", 0.0))]
                )
            ws.append([])

        add_section("Eiendomsmegler", data.get("eiendomsmegler", []))
        add_section("Eiendomsmeglerfullmektig", data.get("eiendomsmeglerfullmektig", []))
        if data.get("unknown"):
            add_section("Ukjent rolle", data.get("unknown", []))
        add_section("Avdelinger", data.get("departments", []), name_key="department_name")

        ws.column_dimensions["A"].width = 36
        ws.column_dimensions["B"].width = 14
        ws.column_dimensions["C"].width = 20
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    async def _fetch_report_data(
        self,
        *,
        department_id: int = DEFAULT_DEPARTMENT_ID,
        year: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        include_vat: bool = False,
    ) -> tuple:
        """Fetch report data and return (report_data_dict, broker_map, ...) for Excel or JSON."""
        if not self._hub.is_configured:
            raise ValueError("Vitec Hub credentials are not configured.")

        installation_id = settings.VITEC_INSTALLATION_ID
        if not installation_id:
            raise ValueError("VITEC_INSTALLATION_ID is not configured.")

        y = year or datetime.now().year
        if from_date:
            from_date = from_date if "T" in from_date else f"{from_date}T00:00:00"
        else:
            from_date = f"{y}-01-01T00:00:00"
        if to_date:
            to_date = to_date if "T" in to_date else f"{to_date}T23:59:59"
        else:
            to_date = datetime.now().strftime("%Y-%m-%dT23:59:59")
        changed_after = from_date[:10] + "T00:00:00"

        # 1. Fetch employees
        employees = await self._hub.get_employees(installation_id)
        broker_map: dict[str, str] = {}
        for emp in employees or []:
            eid = emp.get("employeeId")
            name = emp.get("name")
            if eid and name:
                broker_map[str(eid).strip()] = str(name).strip()

        # 2. Fetch accounting estates
        estates = await self._hub.get_accounting_estates(
            installation_id,
            department_id=department_id,
            changed_after=changed_after,
        )

        estate_address: dict[str, str] = {}
        estate_metadata: dict[str, dict[str, str]] = {}
        brokers_with_sales: set[str] = set()
        for est in estates or []:
            eid = str(est.get("estateId") or "").strip()
            addr = _build_estate_address(est)
            if eid:
                estate_address[eid] = addr or "(ukjent adresse)"
                estate_metadata[eid] = _build_estate_metadata(est)
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

        # 3. Fetch transactions
        transactions = await self._hub.get_accounting_transactions(
            installation_id,
            from_date=from_date,
            to_date=to_date,
            department_id=department_id,
            ledger_type=1,
        )

        # 4. Build broker_estates
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

        # 5. Build report data dict
        report_data = {
            "year": y,
            "department_id": department_id,
            "from_date": from_date,
            "to_date": to_date,
            "from_date_display": _format_date_iso(from_date) or from_date[:10],
            "to_date_display": _format_date_iso(to_date) or to_date[:10],
            "include_vat": include_vat,
            "brokers": [],
        }

        for broker_id in sorted(brokers_with_sales):
            name = broker_map.get(broker_id, broker_id)
            estates_data = broker_estates.get(broker_id, {})
            sale_count = len(estates_data)
            total = 0.0
            properties: list[dict] = []
            for estate_id, txns in sorted(estates_data.items(), key=lambda x: estate_address.get(x[0], x[0])):
                addr = estate_address.get(estate_id, estate_id)
                meta = estate_metadata.get(estate_id, {"property_type": "—", "assignment_type": "—"})
                prop_total = 0.0
                txns_data: list[dict] = []
                for txn in txns:
                    amt = _revenue_amount(
                        float(txn.get("amount") or 0),
                        float(txn.get("vatAmount") or 0),
                        include_vat,
                    )
                    prop_total += amt
                    total += amt
                    txns_data.append(
                        {
                            "posting_date": _format_date_iso(txn.get("postingDate")),
                            "account": txn.get("account"),
                            "description": (txn.get("description") or "")[:80],
                            "amount": round(amt, 2),
                        }
                    )
                properties.append(
                    {
                        "address": addr,
                        "estate_id": estate_id,
                        "property_type": meta["property_type"],
                        "assignment_type": meta["assignment_type"],
                        "total": round(prop_total, 2),
                        "transactions": txns_data,
                    }
                )
            report_data["brokers"].append(
                {
                    "broker_id": broker_id,
                    "name": name,
                    "sale_count": sale_count,
                    "total": round(total, 2),
                    "properties": properties,
                }
            )

        # Exclude brokers with 0 sales (oppgjørsansvarlig from Aktiv Oppgjør / Pacta Oppgjør)
        report_data["brokers"] = [b for b in report_data["brokers"] if b["sale_count"] > 0]
        report_data["total_sales"] = sum(b["sale_count"] for b in report_data["brokers"])
        report_data["total_revenue"] = round(sum(b["total"] for b in report_data["brokers"]), 2)

        return report_data, broker_map, brokers_with_sales, broker_estates, estate_address, estate_metadata, include_vat

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
        estate_metadata: dict[str, dict[str, str]],
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
        ws.merge_cells("A1:E1")
        ws["A1"].font = Font(bold=True, size=14)
        ws.append([f"Avdeling: {department_id}  |  År: {year}  |  Periode: {from_display} - {to_display}"])
        ws.merge_cells("A2:E2")
        ws.append([])

        # Column headers: Megler, Antall salg, Eiendomstype, Oppdragstype, Sum
        headers = ["Megler", "Antall salg", "Eiendomstype", "Oppdragstype", sum_label]
        ws.append(headers)
        header_row = ws.max_row
        for col in range(1, len(headers) + 1):
            ws.cell(row=header_row, column=col).font = Font(bold=True)

        # Data rows with expandable detail
        # Only include brokers with at least one sale
        brokers_sorted = [b for b in sorted(brokers_with_sales) if len(broker_estates.get(b, {})) > 0]
        row = header_row + 1

        for broker_id in brokers_sorted:
            name = broker_map.get(broker_id, broker_id)
            estates = broker_estates.get(broker_id, {})
            sale_count = len(estates)

            total = 0.0
            for estate_txns in estates.values():
                for txn in estate_txns:
                    total += _revenue_amount(
                        float(txn.get("amount") or 0),
                        float(txn.get("vatAmount") or 0),
                        include_vat,
                    )

            # Broker summary row (level 0) - no property/assignment type at broker level
            ws.append([name, sale_count, "", "", round(total, 2)])
            broker_row = row
            row += 1

            # Property and transaction detail (grouped)
            for estate_id, txns in sorted(estates.items(), key=lambda x: estate_address.get(x[0], x[0])):
                addr = estate_address.get(estate_id, estate_id)
                meta = estate_metadata.get(estate_id, {"property_type": "—", "assignment_type": "—"})
                # Property row (level 1)
                ws.append([f"  {addr}", "", meta["property_type"], meta["assignment_type"], ""])
                ws.cell(row=row, column=1).font = Font(italic=True)
                prop_row = row
                row += 1

                # Transaction rows (level 2)
                for txn in txns:
                    amt = _revenue_amount(
                        float(txn.get("amount") or 0),
                        float(txn.get("vatAmount") or 0),
                        include_vat,
                    )
                    post_date = _format_date_iso(txn.get("postingDate"))
                    acc = txn.get("account") or ""
                    desc = (txn.get("description") or "")[:40]
                    ws.append([f"    {post_date} | Konto {acc} | {desc}", "", "", "", round(amt, 2)])
                    row += 1

                # Group property + its transactions
                ws.row_dimensions.group(prop_row, row - 1, outline_level=2, hidden=False)

            # Group broker + all properties
            if row > broker_row + 1:
                ws.row_dimensions.group(broker_row + 1, row - 1, outline_level=1, hidden=False)

        # Total row
        total_revenue = sum(
            sum(
                _revenue_amount(float(t.get("amount") or 0), float(t.get("vatAmount") or 0), include_vat)
                for est_txns in broker_estates.get(b, {}).values()
                for t in est_txns
            )
            for b in brokers_sorted
        )
        total_sales = sum(len(broker_estates.get(b, {})) for b in brokers_sorted)
        ws.append(["Sum", total_sales, "", "", round(total_revenue, 2)])
        total_row = row
        for col in range(1, 6):
            ws.cell(row=total_row, column=col).font = Font(bold=True)

        # Column widths
        ws.column_dimensions["A"].width = 45
        ws.column_dimensions["B"].width = 14
        ws.column_dimensions["C"].width = 18
        ws.column_dimensions["D"].width = 18
        ws.column_dimensions["E"].width = 38

        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue()
