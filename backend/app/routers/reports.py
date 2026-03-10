"""
Reports API

Sales report and other downloadable reports.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.services.sales_report_service import SalesReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/sales-report")
async def get_sales_report(
    year: int | None = Query(None, description="Report year (default: current year)"),
    department_id: int = Query(1120, description="Vitec department ID (Proaktiv Eiendomsmegling AS)"),
) -> Response:
    """
    Export sales report as Excel.

    Brokers who sold properties this year in the given department,
    with vederlag + andre inntekter (hovedbokskonti 3000-3221, 3020-8050).
    """
    try:
        service = SalesReportService()
        excel_bytes = await service.build_report(department_id=department_id, year=year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        if e.status_code == 403:
            raise HTTPException(
                status_code=503,
                detail="Vitec Hub Accounting API er ikke tilgjengelig for denne installasjonen. "
                "Kontakt Vitec for å be om tilgang til Accounting/Estates og Accounting/Transactions.",
            ) from e
        raise

    y = year or datetime.now().year
    filename = f"formidlingsrapport_{department_id}_{y}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
