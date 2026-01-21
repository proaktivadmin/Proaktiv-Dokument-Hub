"""
AuditLog SQLAlchemy Model
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType


class AuditLog(Base):
    """
    Audit log model for tracking user actions.

    Records all significant actions performed on entities
    (templates, tags, categories) for compliance and debugging.
    """

    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Required fields
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'template', 'tag', 'category'

    entity_id: Mapped[uuid.UUID] = mapped_column(GUID, nullable=False)

    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'created', 'updated', 'deleted', 'published', 'downloaded'

    user_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional fields
    details: Mapped[dict | None] = mapped_column(
        JSONType, nullable=True, default=dict
    )  # Additional context (e.g., previous values, IP address)

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
        Index("idx_audit_logs_user", "user_email"),
        Index("idx_audit_logs_action", "action"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(entity={self.entity_type}:{self.entity_id}, action='{self.action}', user='{self.user_email}')>"
        )
