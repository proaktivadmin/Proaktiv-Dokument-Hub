"""
Report access audit log.

Retention policy:
- Rows older than 90 days should be purged.
- ip_address should be redacted (set NULL) after 30 days (GDPR: IP is PII).
- params_json must never contain auth tokens, cookies, or credentials.

Cleanup queries (run manually or via future scheduler):
    DELETE FROM report_access_log WHERE created_at < now() - interval '90 days';
    UPDATE report_access_log SET ip_address = NULL
     WHERE created_at < now() - interval '30 days'
       AND ip_address IS NOT NULL;
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base, JSONType


class ReportAccessLog(Base):
    """Tracks who accessed report data, downloads, and subscription sends."""

    __tablename__ = "report_access_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_email: Mapped[str] = mapped_column(String(200), nullable=False, default="anonymous")
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False, default="view")
    params_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_report_access_log_user", "user_email"),
        Index("idx_report_access_log_created", "created_at"),
    )
