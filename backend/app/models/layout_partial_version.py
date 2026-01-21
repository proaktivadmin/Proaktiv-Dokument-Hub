"""
LayoutPartialVersion and LayoutPartialDefault SQLAlchemy Models

Version history and default assignment rules for layout partials.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.layout_partial import LayoutPartial


class LayoutPartialVersion(Base):
    """
    LayoutPartialVersion model for tracking version history.

    Each version stores the complete HTML content at that point in time.
    """

    __tablename__ = "layout_partial_versions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    partial_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("layout_partials.id", ondelete="CASCADE"), nullable=False
    )

    # Version info
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    change_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    partial: Mapped["LayoutPartial"] = relationship("LayoutPartial", back_populates="versions")

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint("partial_id", "version_number", name="uq_layout_partial_version"),
        Index("idx_layout_partial_versions_partial_id", "partial_id"),
    )

    def __repr__(self) -> str:
        return f"<LayoutPartialVersion(partial_id={self.partial_id}, version={self.version_number})>"


class LayoutPartialDefault(Base):
    """
    LayoutPartialDefault model for assignment rules.

    Defines which partial should be used as default based on:
    - Scope 'all': Universal default
    - Scope 'category': Default for a specific category
    - Scope 'medium': Default for a specific medium (pdf, email, sms)
    """

    __tablename__ = "layout_partial_defaults"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    partial_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("layout_partials.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )

    # Scope and priority
    scope: Mapped[str] = mapped_column(String(20), nullable=False, default="all")  # 'all' | 'category' | 'medium'
    medium: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 'pdf' | 'email' | 'sms'
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    partial: Mapped["LayoutPartial"] = relationship("LayoutPartial", back_populates="defaults")

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="layout_partial_defaults")

    # Indexes
    __table_args__ = (
        Index("idx_layout_partial_defaults_partial_id", "partial_id"),
        Index("idx_layout_partial_defaults_scope", "scope"),
    )

    def __repr__(self) -> str:
        return f"<LayoutPartialDefault(partial_id={self.partial_id}, scope='{self.scope}')>"

    @property
    def scope_description(self) -> str:
        """Return human-readable scope description."""
        if self.scope == "all":
            return "Alle maler"
        elif self.scope == "category" and self.category:
            return f"Kategori: {self.category.name}"
        elif self.scope == "medium" and self.medium:
            medium_names = {"pdf": "PDF-dokumenter", "email": "E-post", "sms": "SMS"}
            return medium_names.get(self.medium, self.medium)
        return "Ukjent"
