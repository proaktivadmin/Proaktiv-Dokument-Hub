"""
SyncSession SQLAlchemy Model

Stores preview data and decisions for manual Vitec sync review.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base, GUID, JSONType


class SyncSession(Base):
    """Session storage for Vitec sync preview + decisions."""

    __tablename__ = "sync_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )  # pending | committed | expired | cancelled

    preview_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType,
        nullable=True,
        default=dict,
    )
    decisions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType,
        nullable=True,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_sync_sessions_status", "status"),
        Index("idx_sync_sessions_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<SyncSession(id={self.id}, status='{self.status}')>"
