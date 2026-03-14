"""
Reports API

Sales report and other downloadable reports.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory, get_db
from app.models.report_access_log import ReportAccessLog
from app.models.report_subscription import ReportSubscription
from app.schemas.reports import (
    BudgetComparisonResponse,
    ReportBudgetCreate,
    ReportBudgetResponse,
    ReportBudgetUpdate,
    ReportSalesSyncEventResponse,
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

_SAFE_PARAM_KEYS = frozenset(
    {
        "year",
        "department_id",
        "from_date",
        "to_date",
        "include_vat",
        "department_ids",
        "top_n",
        "since_id",
        "limit",
        "active_only",
    }
)


async def _write_audit_log_safe(
    request: Request,
    *,
    action: str = "view",
    extra_params: dict | None = None,
) -> None:
    """Fire-and-forget audit log entry. Never raises, never blocks the response."""
    try:
        await _write_audit_log_inner(request, action=action, extra_params=extra_params)
    except Exception:
        logger.debug("Audit log write failed (outer guard)", exc_info=True)


async def _write_audit_log_inner(
    request: Request,
    *,
    action: str = "view",
    extra_params: dict | None = None,
) -> None:
    try:
        email = "anonymous"
        token = request.cookies.get("session")
        if token:
            try:
                from app.config import settings

                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                email = payload.get("sub") or "anonymous"
            except Exception:
                pass

        params = {k: v for k, v in request.query_params.items() if k in _SAFE_PARAM_KEYS}
        if extra_params:
            params.update(extra_params)

        ip = request.client.host if request.client else None

        async with async_session_factory() as db:
            db.add(
                ReportAccessLog(
                    user_email=email,
                    endpoint=request.url.path,
                    action=action,
                    params_json=params,
                    ip_address=ip,
                )
            )
            await db.commit()
    except Exception:
        logger.debug("Failed to write report access log", exc_info=True)


@router.get("/sales-report/data")
async def get_sales_report_data(
    request: Request,
    year: int | None = Query(None, description="Report year (default: current year)"),
    department_id: int = Query(1120, description="Vitec department ID"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
):
    """
    Get sales report data as JSON for dashboard display.
    """
    await _write_audit_log_safe(request, action="view")
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
    request: Request,
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
    await _write_audit_log_safe(request, action="download")
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
    request: Request,
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
):
    await _write_audit_log_safe(request, action="view")
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
    request: Request,
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
    top_n: int = Query(5, ge=1, le=20),
):
    await _write_audit_log_safe(request, action="view")
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
    request: Request,
    year: int | None = Query(None, description="Report year (default: current year)"),
    from_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_vat: bool = Query(False, description="Include VAT in revenue sums"),
    department_ids: list[int] | None = Query(None, description="Optional list of department IDs"),
    top_n: int = Query(5, ge=1, le=20),
) -> Response:
    await _write_audit_log_safe(request, action="download")
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


@router.get("/cache-events", response_model=list[ReportSalesSyncEventResponse])
async def list_cache_events(
    department_id: int | None = Query(None),
    since_id: int | None = Query(None, ge=1),
    limit: int = Query(100, ge=1, le=500),
):
    try:
        service = SalesReportService()
        return await service.list_cache_events(department_id=department_id, since_id=since_id, limit=limit)
    except Exception as exc:
        logger.exception("list_cache_events failed: %s", exc)
        hint = (
            "Ensure migrations 20260312_0001 and 20260312_0002 are applied to the database. "
            "See .cursor/rules/database-migrations.mdc for manual Railway migration steps."
        )
        raise HTTPException(status_code=500, detail=f"{exc!s}. {hint}") from exc


@router.get("/cache-events/stream")
async def stream_cache_events(
    department_id: int | None = Query(None),
    since_id: int | None = Query(None, ge=1),
    poll_interval_seconds: float = Query(2.0, ge=0.5, le=30.0),
    max_seconds: int = Query(55, ge=0, le=300),
):
    service = SalesReportService()

    async def event_stream():
        current_since = since_id
        started = datetime.now(timezone.utc)  # noqa: UP017
        try:
            while (datetime.now(timezone.utc) - started).total_seconds() < max_seconds:  # noqa: UP017
                events = await service.list_cache_events(
                    department_id=department_id,
                    since_id=current_since,
                    limit=200,
                )
                for event in events:
                    current_since = max(current_since or 0, int(event.id))
                    payload = {
                        "id": event.id,
                        "installation_id": event.installation_id,
                        "department_id": event.department_id,
                        "event_type": event.event_type,
                        "from_date": event.from_date,
                        "to_date": event.to_date,
                        "estates_upserted": event.estates_upserted,
                        "transactions_upserted": event.transactions_upserted,
                        "payload": event.payload_json or {},
                        "created_at": event.created_at.isoformat() if event.created_at else None,
                    }
                    yield f"id: {event.id}\nevent: {event.event_type}\ndata: {json.dumps(payload)}\n\n"
                yield ": keepalive\n\n"
                await asyncio.sleep(poll_interval_seconds)
        except Exception as exc:
            logger.exception("stream_cache_events failed: %s", exc)
            yield f"event: error\ndata: {json.dumps({'error': str(exc), 'hint': 'Ensure migrations 20260312_0001 and 20260312_0002 are applied.'})}\n\n"
            raise

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
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
    request: Request,
    subscription_id: UUID,
    recipient: str | None = Query(None, description="Optional single test recipient"),
    db: AsyncSession = Depends(get_db),
):
    await _write_audit_log_safe(
        request, action="subscription_send", extra_params={"subscription_id": str(subscription_id)}
    )
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
