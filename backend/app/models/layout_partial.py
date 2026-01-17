"""
LayoutPartial SQLAlchemy Model

Represents reusable header, footer, and signature templates.
"""

from sqlalchemy import String, Text, Boolean, DateTime, Index, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
import uuid

from app.models.base import Base, GUID


class LayoutPartial(Base):
    """
    Layout partial model for headers, footers, and signatures.
    
    Stores reusable HTML snippets that can be applied to templates:
    - header: Document header for PDF templates
    - footer: Document footer for PDF templates  
    - signature: Email or SMS signature
    
    Each partial has a context (pdf/email/sms/all) to match the appropriate channel.
    """
    
    __tablename__ = "layout_partials"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Partial identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'header' | 'footer' | 'signature'
    context: Mapped[str] = mapped_column(String(50), default='all')  # 'pdf' | 'email' | 'sms' | 'all'
    
    # Optional: Document type for specialized footers (kontrakt, skjote, sikring, etc.)
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
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
    # Note: Constraints are updated via migration 0006 to include 'signature' type and 'sms' context
    __table_args__ = (
        Index("idx_layout_partials_type", "type"),
        Index("idx_layout_partials_context", "context"),
        Index("idx_layout_partials_is_default", "is_default"),
        Index("idx_layout_partials_document_type", "document_type"),
        CheckConstraint("type IN ('header', 'footer', 'signature')", name="ck_layout_partial_type_v2"),
        CheckConstraint("context IN ('pdf', 'email', 'sms', 'all')", name="ck_layout_partial_context_v2"),
    )
    
    def __repr__(self) -> str:
        return f"<LayoutPartial(name='{self.name}', type='{self.type}', context='{self.context}')>"
