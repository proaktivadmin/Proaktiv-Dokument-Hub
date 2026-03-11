"""
Report Budget Service
"""

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report_budget import ReportBudget
from app.schemas.reports import ReportBudgetCreate, ReportBudgetUpdate
from app.services.sales_report_service import SalesReportService


class ReportBudgetService:
    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        department_id: int | None = None,
        year: int | None = None,
    ) -> list[ReportBudget]:
        query = select(ReportBudget)
        if department_id is not None:
            query = query.where(ReportBudget.department_id == department_id)
        if year is not None:
            query = query.where(ReportBudget.year == year)
        query = query.order_by(ReportBudget.department_id.asc(), ReportBudget.year.asc(), ReportBudget.month.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, payload: ReportBudgetCreate) -> ReportBudget:
        # Enforce uniqueness for (department_id, year, month), including month=None.
        existing_query = select(ReportBudget).where(
            and_(
                ReportBudget.department_id == payload.department_id,
                ReportBudget.year == payload.year,
                ReportBudget.month.is_(payload.month) if payload.month is None else ReportBudget.month == payload.month,
            )
        )
        existing = (await db.execute(existing_query)).scalar_one_or_none()
        if existing:
            existing.budget_amount = payload.budget_amount
            await db.flush()
            await db.refresh(existing)
            return existing

        item = ReportBudget(
            department_id=payload.department_id,
            year=payload.year,
            month=payload.month,
            budget_amount=payload.budget_amount,
        )
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def update(db: AsyncSession, budget_id: str, payload: ReportBudgetUpdate) -> ReportBudget | None:
        item = await db.get(ReportBudget, budget_id)
        if not item:
            return None
        item.budget_amount = payload.budget_amount
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete(db: AsyncSession, budget_id: str) -> bool:
        item = await db.get(ReportBudget, budget_id)
        if not item:
            return False
        await db.delete(item)
        await db.flush()
        return True

    @staticmethod
    async def comparison(
        db: AsyncSession,
        *,
        department_id: int,
        year: int,
        include_vat: bool = False,
    ) -> dict:
        budgets = await ReportBudgetService.list(db, department_id=department_id, year=year)
        by_month: dict[int, float] = dict.fromkeys(range(1, 13), 0.0)
        yearly_budget = 0.0
        for b in budgets:
            if b.month is None:
                yearly_budget += float(b.budget_amount or 0.0)
            else:
                by_month[int(b.month)] = float(b.budget_amount or 0.0)

        if yearly_budget > 0:
            allocated = sum(by_month.values())
            if allocated < yearly_budget:
                missing_each = (yearly_budget - allocated) / 12.0
                for m in range(1, 13):
                    by_month[m] += missing_each

        sales = SalesReportService()
        month_rows: list[dict] = []
        ytd_actual = 0.0
        ytd_budget = 0.0
        now = datetime.now()
        current_month = 12 if year < now.year else now.month

        for m in range(1, 13):
            from_date = f"{year}-{m:02d}-01"
            if m == 12:
                to_date = f"{year}-12-31"
            else:
                to_date = f"{year}-{m + 1:02d}-01"
                to_date = (datetime.fromisoformat(to_date) - datetime.resolution).strftime("%Y-%m-%d")
            data = await sales.get_report_data(
                department_id=department_id,
                from_date=from_date,
                to_date=to_date,
                include_vat=include_vat,
                year=year,
            )
            actual = float(data.get("total_revenue") or 0.0)
            budget = float(by_month[m] or 0.0)
            variance = actual - budget
            achieved = (actual / budget * 100.0) if budget > 0 else 0.0
            month_rows.append(
                {
                    "month": m,
                    "actual": round(actual, 2),
                    "budget": round(budget, 2),
                    "variance": round(variance, 2),
                    "achieved_percent": round(achieved, 2),
                }
            )
            if m <= current_month:
                ytd_actual += actual
                ytd_budget += budget

        ytd_variance = ytd_actual - ytd_budget
        ytd_achieved = (ytd_actual / ytd_budget * 100.0) if ytd_budget > 0 else 0.0
        projected_year_end = (ytd_actual / current_month * 12.0) if current_month > 0 else 0.0

        status = "On track"
        if ytd_budget > 0:
            ratio = ytd_actual / ytd_budget
            if ratio < 0.95:
                status = "Behind"
            elif ratio > 1.05:
                status = "Ahead"

        return {
            "department_id": department_id,
            "year": year,
            "include_vat": include_vat,
            "months": month_rows,
            "ytd_actual": round(ytd_actual, 2),
            "ytd_budget": round(ytd_budget, 2),
            "ytd_variance": round(ytd_variance, 2),
            "ytd_achieved_percent": round(ytd_achieved, 2),
            "projected_year_end": round(projected_year_end, 2),
            "status": status,
        }
