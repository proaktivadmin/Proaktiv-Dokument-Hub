"""
Pydantic schemas for reports endpoints.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ReportBudgetBase(BaseModel):
    department_id: int = Field(..., ge=1)
    year: int = Field(..., ge=2000, le=2100)
    month: int | None = Field(None, ge=1, le=12)
    budget_amount: float = Field(..., ge=0)


class ReportBudgetCreate(ReportBudgetBase):
    pass


class ReportBudgetUpdate(BaseModel):
    budget_amount: float = Field(..., ge=0)


class ReportBudgetResponse(ReportBudgetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetComparisonMonth(BaseModel):
    month: int
    actual: float
    budget: float
    variance: float
    achieved_percent: float


class BudgetComparisonResponse(BaseModel):
    department_id: int
    year: int
    include_vat: bool
    months: list[BudgetComparisonMonth]
    ytd_actual: float
    ytd_budget: float
    ytd_variance: float
    ytd_achieved_percent: float
    projected_year_end: float
    status: Literal["On track", "Behind", "Ahead"]


class ReportSubscriptionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    report_type: Literal["best_performers", "franchise_summary"] = "best_performers"
    cadence: Literal["weekly", "monthly"] = "weekly"
    recipients: list[str] = Field(..., min_length=1)
    department_ids: list[int] = Field(default_factory=list)
    include_vat: bool = False
    day_of_week: int = Field(5, ge=1, le=7)
    day_of_month: int = Field(1, ge=1, le=28)
    send_hour: int = Field(8, ge=0, le=23)
    timezone: str = "Europe/Oslo"
    is_active: bool = True


class ReportSubscriptionCreate(ReportSubscriptionBase):
    pass


class ReportSubscriptionUpdate(ReportSubscriptionBase):
    pass


class ReportSubscriptionResponse(BaseModel):
    name: str
    report_type: Literal["best_performers", "franchise_summary"]
    cadence: Literal["weekly", "monthly"]
    recipients: list[str] = Field(default_factory=list, alias="recipients_json")
    department_ids: list[int] = Field(default_factory=list, alias="department_ids_json")
    include_vat: bool
    day_of_week: int
    day_of_month: int
    send_hour: int
    timezone: str
    is_active: bool
    id: UUID
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    last_status: str | None = None
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ReportDataSourceInfo(BaseModel):
    name: str
    label: str
    coverage: str
    row_count: int = 0


class ReportScopeMetadata(BaseModel):
    accounts_included: list[str]
    account_categories: dict[str, list[str]]
    estate_statuses: str = "40-48 (solgt/overtatt)"
    vat_handling: str
    date_range: dict[str, str]
    department_filter: int | None = None
    last_synced_at: str | None = None
    data_sources: list[ReportDataSourceInfo]
    brokers_filter: str = "only brokers with sales in period"
    data_freshness_note: str = "Current month re-synced on every load; past months cached"
    validation_warnings_count: int = 0


class ReportSalesSyncEventResponse(BaseModel):
    id: int
    installation_id: str
    department_id: int
    event_type: str
    from_date: str
    to_date: str
    estates_upserted: int
    transactions_upserted: int
    payload: dict = Field(default_factory=dict, alias="payload_json")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
