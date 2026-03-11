"""
Report Subscription Service
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report_subscription import ReportSubscription
from app.schemas.reports import ReportSubscriptionCreate, ReportSubscriptionUpdate


def _next_run_at(
    *,
    cadence: str,
    day_of_week: int,
    day_of_month: int,
    send_hour: int,
    now: datetime | None = None,
) -> datetime:
    current = now or datetime.utcnow()
    candidate = current.replace(hour=send_hour, minute=0, second=0, microsecond=0)
    if cadence == "monthly":
        day = min(max(day_of_month, 1), 28)
        this_month = candidate.replace(day=day)
        if this_month > current:
            return this_month
        month = candidate.month + 1
        year = candidate.year
        if month > 12:
            month = 1
            year += 1
        return candidate.replace(year=year, month=month, day=day)

    # Weekly default
    target_iso = min(max(day_of_week, 1), 7)
    days_ahead = target_iso - candidate.isoweekday()
    if days_ahead < 0 or (days_ahead == 0 and candidate <= current):
        days_ahead += 7
    return candidate + timedelta(days=days_ahead)


class ReportSubscriptionService:
    @staticmethod
    async def list(db: AsyncSession, *, active_only: bool = False) -> list[ReportSubscription]:
        query = select(ReportSubscription).order_by(ReportSubscription.created_at.desc())
        if active_only:
            query = query.where(ReportSubscription.is_active.is_(True))
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, payload: ReportSubscriptionCreate) -> ReportSubscription:
        item = ReportSubscription(
            name=payload.name,
            report_type=payload.report_type,
            cadence=payload.cadence,
            recipients_json=payload.recipients,
            department_ids_json=payload.department_ids,
            include_vat=payload.include_vat,
            day_of_week=payload.day_of_week,
            day_of_month=payload.day_of_month,
            send_hour=payload.send_hour,
            timezone=payload.timezone,
            is_active=payload.is_active,
            next_run_at=_next_run_at(
                cadence=payload.cadence,
                day_of_week=payload.day_of_week,
                day_of_month=payload.day_of_month,
                send_hour=payload.send_hour,
            ),
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def update(db: AsyncSession, subscription_id: str, payload: ReportSubscriptionUpdate) -> ReportSubscription | None:
        item = await db.get(ReportSubscription, subscription_id)
        if not item:
            return None
        item.name = payload.name
        item.report_type = payload.report_type
        item.cadence = payload.cadence
        item.recipients_json = payload.recipients
        item.department_ids_json = payload.department_ids
        item.include_vat = payload.include_vat
        item.day_of_week = payload.day_of_week
        item.day_of_month = payload.day_of_month
        item.send_hour = payload.send_hour
        item.timezone = payload.timezone
        item.is_active = payload.is_active
        item.next_run_at = _next_run_at(
            cadence=item.cadence,
            day_of_week=item.day_of_week,
            day_of_month=item.day_of_month,
            send_hour=item.send_hour,
        )
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete(db: AsyncSession, subscription_id: str) -> bool:
        item = await db.get(ReportSubscription, subscription_id)
        if not item:
            return False
        await db.delete(item)
        await db.flush()
        return True

    @staticmethod
    async def due_subscriptions(db: AsyncSession) -> list[ReportSubscription]:
        now = datetime.utcnow()
        query = select(ReportSubscription).where(
            ReportSubscription.is_active.is_(True),
            ReportSubscription.next_run_at.is_not(None),
            ReportSubscription.next_run_at <= now,
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def mark_run(item: ReportSubscription, *, success: bool, error: str | None = None) -> None:
        now = datetime.utcnow()
        item.last_run_at = now
        item.last_status = "success" if success else "failed"
        item.last_error = error
        item.next_run_at = _next_run_at(
            cadence=item.cadence,
            day_of_week=item.day_of_week,
            day_of_month=item.day_of_month,
            send_hour=item.send_hour,
            now=now + timedelta(minutes=1),
        )
