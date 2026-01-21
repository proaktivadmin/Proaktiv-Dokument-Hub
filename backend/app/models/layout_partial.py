"""
LayoutPartial SQLAlchemy Model

Represents reusable header, footer, signature, and stilark templates.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base

if TYPE_CHECKING:
    from app.models.layout_partial_version import LayoutPartialDefault, LayoutPartialVersion


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
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Partial identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'header' | 'footer' | 'signature'
    context: Mapped[str] = mapped_column(String(50), default="all")  # 'pdf' | 'email' | 'sms' | 'all'

    # Optional: Document type for specialized footers (kontrakt, skjote, sikring, etc.)
    document_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Content
    html_content: Mapped[str] = mapped_column(Text, nullable=False)

    # Default flag
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit fields
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    versions: Mapped[list["LayoutPartialVersion"]] = relationship(
        "LayoutPartialVersion", back_populates="partial", cascade="all, delete-orphan", lazy="selectin"
    )

    defaults: Mapped[list["LayoutPartialDefault"]] = relationship(
        "LayoutPartialDefault", back_populates="partial", cascade="all, delete-orphan", lazy="selectin"
    )

    # Indexes and constraints
    # Note: Constraints are updated via migration 0005 to include 'signature' and 'stilark' types
    __table_args__ = (
        Index("idx_layout_partials_type", "type"),
        Index("idx_layout_partials_context", "context"),
        Index("idx_layout_partials_is_default", "is_default"),
        Index("idx_layout_partials_document_type", "document_type"),
        CheckConstraint("type IN ('header', 'footer', 'signature', 'stilark')", name="ck_layout_partial_type_v2"),
        CheckConstraint("context IN ('pdf', 'email', 'sms', 'all')", name="ck_layout_partial_context_v2"),
    )

    def __repr__(self) -> str:
        return f"<LayoutPartial(name='{self.name}', type='{self.type}', context='{self.context}')>"

    @property
    def current_version(self) -> int:
        """Return the current version number."""
        if not self.versions:
            return 1
        return max(v.version_number for v in self.versions)
