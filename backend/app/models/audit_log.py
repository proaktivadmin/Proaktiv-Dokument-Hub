"""
AuditLog SQLAlchemy Model
"""

from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import uuid

from app.models.base import Base


class AuditLog(Base):
    """
    Audit log model for tracking user actions.
    
    Records all significant actions performed on entities
    (templates, tags, categories) for compliance and debugging.
    """
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Required fields
    entity_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # 'template', 'tag', 'category'
    
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        nullable=False
    )
    
    action: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )  # 'created', 'updated', 'deleted', 'published', 'downloaded'
    
    user_email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Optional fields
    details: Mapped[Optional[dict]] = mapped_column(
        JSONB, 
        nullable=True,
        default=dict
    )  # Additional context (e.g., previous values, IP address)
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        index=True
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
        Index("idx_audit_logs_user", "user_email"),
        Index("idx_audit_logs_action", "action"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(entity={self.entity_type}:{self.entity_id}, action='{self.action}', user='{self.user_email}')>"

