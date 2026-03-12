"""
Cached Vitec sales reporting data models.

Multi-source architecture: the ``data_source`` column on estate and transaction
cache tables discriminates between ingestion origins so historical imports and
future KPI sources can coexist with live Vitec Next data.

Current values: ``vitec_next`` (live API sync), ``legacy_import`` (deferred).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base, JSONType

DATA_SOURCE_VITEC_NEXT = "vitec_next"
DATA_SOURCE_LEGACY_IMPORT = "legacy_import"


class ReportSalesEstateCache(Base):
    """Cached estate metadata used by reports."""

    __tablename__ = "report_sales_estate_cache"

    estate_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    installation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    estate_id: Mapped[str] = mapped_column(String(64), nullable=False)
    data_source: Mapped[str] = mapped_column(
        String(30), nullable=False, default=DATA_SOURCE_VITEC_NEXT, server_default=DATA_SOURCE_VITEC_NEXT,
    )
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    property_type: Mapped[str] = mapped_column(String(100), nullable=False, default="—")
    assignment_type: Mapped[str] = mapped_column(String(100), nullable=False, default="—")
    brokers_json: Mapped[list[dict]] = mapped_column("brokers", JSONType, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_report_sales_estate_cache_dept", "department_id"),
        Index("idx_report_sales_estate_cache_installation", "installation_id"),
        Index("idx_report_sales_estate_cache_sold", "sold_at"),
        Index("idx_report_sales_estate_cache_source", "data_source"),
        Index("idx_report_sales_estate_cache_dept_source", "department_id", "data_source"),
    )


class ReportSalesTransactionCache(Base):
    """Cached accounting transaction rows used by reports."""

    __tablename__ = "report_sales_transaction_cache"

    transaction_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    installation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_source: Mapped[str] = mapped_column(
        String(30), nullable=False, default=DATA_SOURCE_VITEC_NEXT, server_default=DATA_SOURCE_VITEC_NEXT,
    )
    posting_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    estate_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_report_sales_tx_cache_dept_date", "department_id", "posting_date"),
        Index("idx_report_sales_tx_cache_installation", "installation_id"),
        Index("idx_report_sales_tx_cache_user", "user_id"),
        Index("idx_report_sales_tx_cache_estate", "estate_id"),
        Index("idx_report_sales_tx_cache_account", "account"),
        Index("idx_report_sales_tx_cache_source", "data_source"),
        Index("idx_report_sales_tx_cache_dept_source_date", "department_id", "data_source", "posting_date"),
    )


class ReportSalesCacheState(Base):
    """Sync cursors/state for incremental Vitec report caching."""

    __tablename__ = "report_sales_cache_state"

    state_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    installation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    last_estates_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    month_sync_json: Mapped[dict] = mapped_column("month_sync", JSONType, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("idx_report_sales_cache_state_dept", "department_id"),
        Index("idx_report_sales_cache_state_installation", "installation_id"),
    )


class ReportSalesSyncEvent(Base):
    """Outbox-style sync events for realtime subscriptions."""

    __tablename__ = "report_sales_sync_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, default="cache_sync")
    from_date: Mapped[str] = mapped_column(String(32), nullable=False)
    to_date: Mapped[str] = mapped_column(String(32), nullable=False)
    estates_upserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    transactions_upserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_json: Mapped[dict] = mapped_column("payload", JSONType, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_report_sales_sync_events_created", "created_at"),
        Index("idx_report_sales_sync_events_dept_created", "department_id", "created_at"),
        Index("idx_report_sales_sync_events_installation", "installation_id"),
    )
