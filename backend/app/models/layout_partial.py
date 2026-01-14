"""
LayoutPartial SQLAlchemy Model

Represents reusable header and footer templates.
"""

from sqlalchemy import String, Text, Boolean, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid

from app.models.base import Base


class LayoutPartial(Base):
    """
    Layout partial model for headers and footers.
    
    Stores reusable header and footer HTML that can be applied to templates.
    Each partial has a type (header/footer) and context (pdf/email/all).
    """
    
    __tablename__ = "layout_partials"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Partial identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'header' | 'footer'
    context: Mapped[str] = mapped_column(String(50), default='all')  # 'pdf' | 'email' | 'all'
    
    # Content
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Default flag
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Audit fields
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_layout_partials_type", "type"),
        Index("idx_layout_partials_context", "context"),
        Index("idx_layout_partials_is_default", "is_default"),
        CheckConstraint("type IN ('header', 'footer')", name="ck_layout_partial_type"),
        CheckConstraint("context IN ('pdf', 'email', 'all')", name="ck_layout_partial_context"),
    )
    
    def __repr__(self) -> str:
        return f"<LayoutPartial(name='{self.name}', type='{self.type}')>"
