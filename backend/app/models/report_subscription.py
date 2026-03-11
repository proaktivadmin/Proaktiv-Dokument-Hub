"""
Report Subscription SQLAlchemy Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType


class ReportSubscription(Base):
    """Scheduled report delivery subscription."""

    __tablename__ = "report_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, default="best_performers")
    cadence: Mapped[str] = mapped_column(String(20), nullable=False, default="weekly")
    recipients_json: Mapped[list[str]] = mapped_column("recipients", JSONType, nullable=False, default=list)
    department_ids_json: Mapped[list[int]] = mapped_column("department_ids", JSONType, nullable=False, default=list)
    include_vat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # ISO 1-7, Friday by default
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    send_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Europe/Oslo")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_report_subscriptions_active", "is_active"),
        Index("idx_report_subscriptions_next_run", "next_run_at"),
        Index("idx_report_subscriptions_cadence", "cadence"),
    )
