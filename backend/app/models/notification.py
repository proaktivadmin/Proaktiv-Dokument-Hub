"""
Notification SQLAlchemy Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType


class Notification(Base):
    """
    Notification model for sync-related events.

    Stores alerts for employee/office sync changes and errors.
    """

    __tablename__ = "notifications"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Required fields
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'employee', 'office', 'sync'
    entity_id: Mapped[uuid.UUID | None] = mapped_column(GUID, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_notifications_unread", "is_read"),
        Index("idx_notifications_created", "created_at"),
        Index("idx_notifications_type", "type"),
        Index("idx_notifications_entity", "entity_type", "entity_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Notification(type='{self.type}', entity={self.entity_type}:{self.entity_id}, "
            f"severity='{self.severity}', read={self.is_read})>"
        )
