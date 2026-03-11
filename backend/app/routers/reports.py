"""
Reports API

Sales report and other downloadable reports.
"""

import logging
import os
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report_subscription import ReportSubscription
from app.schemas.reports import (
    BudgetComparisonResponse,
    ReportBudgetCreate,
    ReportBudgetResponse,
    ReportBudgetUpdate,
    ReportSubscriptionCreate,
    ReportSubscriptionResponse,
    ReportSubscriptionUpdate,
)
from app.services.report_budget_service import ReportBudgetService
from app.services.report_delivery_service import ReportDeliveryService
from app.services.report_subscription_service import ReportSubscriptionService
from app.services.sales_report_service import SalesReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/sales-report/data")
async def get_sales_report_data(
    year: int | None = Query(None, description="Report year (default: current year)"),
    department_id: int = Query(1120, description="Vitec department ID"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
):
    """
    Get sales report data as JSON for dashboard display.
    """
    try:
        service = SalesReportService()
        data = await service.get_report_data(
            department_id=department_id,
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
        )
        return data
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


@router.get("/sales-report")
async def get_sales_report(
    year: int | None = Query(None, description="Report year (default: current year)"),
    department_id: int = Query(1120, description="Vitec department ID (Proaktiv Eiendomsmegling AS)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums (default: exclude)"),
) -> Response:
    """
    Export sales report as Excel.

    Brokers who sold properties this year in the given department,
    with vederlag + andre inntekter (hovedbokskonti 3000-3221, 3020-8050).
    """
    try:
        service = SalesReportService()
        excel_bytes = await service.build_report(
            department_id=department_id,
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
        )
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


@router.get("/sales-report/franchise")
async def get_franchise_report_data(
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
):
    service = SalesReportService()
    try:
        return await service.get_franchise_report_data(
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
            department_ids=department_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/best-performers")
async def get_best_performers(
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
    top_n: int = Query(5, ge=1, le=20),
):
    service = SalesReportService()
    try:
        return await service.get_best_performers_data(
            year=year,
            from_date=from_date,
            to_date=to_date,
            include_vat=include_vat,
            department_ids=department_ids,
            top_n=top_n,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/best-performers/export")
async def download_best_performers(
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
    top_n: int = Query(5, ge=1, le=20),
) -> Response:
    service = SalesReportService()
    excel = await service.build_best_performers_report(
        year=year,
        from_date=from_date,
        to_date=to_date,
        include_vat=include_vat,
        department_ids=department_ids,
        top_n=top_n,
    )
    return Response(
        content=excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="best_performers.xlsx"',
        },
    )


@router.get("/budgets", response_model=list[ReportBudgetResponse])
async def list_budgets(
    year: int | None = Query(None),
    department_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await ReportBudgetService.list(db, year=year, department_id=department_id)


@router.post("/budgets", response_model=ReportBudgetResponse)
async def create_budget(payload: ReportBudgetCreate, db: AsyncSession = Depends(get_db)):
    return await ReportBudgetService.create(db, payload)


@router.put("/budgets/{budget_id}", response_model=ReportBudgetResponse)
async def update_budget(
    budget_id: UUID,
    payload: ReportBudgetUpdate,
    db: AsyncSession = Depends(get_db),
):
    item = await ReportBudgetService.update(db, str(budget_id), payload)
    if not item:
        raise HTTPException(status_code=404, detail="Budget not found")
    return item


@router.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await ReportBudgetService.delete(db, str(budget_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"success": True}


@router.get("/budgets/comparison", response_model=BudgetComparisonResponse)
async def budget_comparison(
    department_id: int = Query(...),
    year: int = Query(...),
    include_vat: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    return await ReportBudgetService.comparison(db, department_id=department_id, year=year, include_vat=include_vat)


@router.get("/subscriptions", response_model=list[ReportSubscriptionResponse])
async def list_subscriptions(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    return await ReportSubscriptionService.list(db, active_only=active_only)


@router.post("/subscriptions", response_model=ReportSubscriptionResponse)
async def create_subscription(payload: ReportSubscriptionCreate, db: AsyncSession = Depends(get_db)):
    return await ReportSubscriptionService.create(db, payload)


@router.put("/subscriptions/{subscription_id}", response_model=ReportSubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    payload: ReportSubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
):
    item = await ReportSubscriptionService.update(db, str(subscription_id), payload)
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return item


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await ReportSubscriptionService.delete(db, str(subscription_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"success": True}


@router.post("/subscriptions/{subscription_id}/test-send")
async def test_send_subscription(
    subscription_id: UUID,
    recipient: str | None = Query(None, description="Optional single test recipient"),
    db: AsyncSession = Depends(get_db),
):
    item = await db.get(ReportSubscription, str(subscription_id))
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")

    delivery = ReportDeliveryService()
    sent = await delivery.send_subscription(item, override_recipient=recipient)
    if not sent:
        raise HTTPException(status_code=500, detail="Could not send test email")
    return {"success": True}


@router.post("/subscriptions/run-due")
async def run_due_subscriptions(
    db: AsyncSession = Depends(get_db),
    x_scheduler_token: str | None = Header(None),
):
    expected = os.getenv("REPORTS_SCHEDULER_TOKEN", "")
    if expected and x_scheduler_token != expected:
        raise HTTPException(status_code=401, detail="Invalid scheduler token")

    due = await ReportSubscriptionService.due_subscriptions(db)
    delivery = ReportDeliveryService()
    sent = 0
    failed = 0
    for item in due:
        try:
            ok = await delivery.send_subscription(item)
            ReportSubscriptionService.mark_run(item, success=ok, error=None if ok else "send_failed")
            sent += int(ok)
            failed += int(not ok)
        except Exception as exc:  # noqa: BLE001
            ReportSubscriptionService.mark_run(item, success=False, error=str(exc)[:500])
            failed += 1
    return {"processed": len(due), "sent": sent, "failed": failed}
