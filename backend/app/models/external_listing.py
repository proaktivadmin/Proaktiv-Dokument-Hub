"""
ExternalListing SQLAlchemy Model

Tracks third-party directory listings for offices and employees.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.office import Office


class ExternalListing(Base):
    """
    ExternalListing model for tracking third-party directory entries.

    Supports various sources like Finn, Anbudstjenester, Google,
    1881, Gulesider, etc. with verification status tracking.
    """

    __tablename__ = "external_listings"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Link to office or employee (one should be set)
    office_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("offices.id", ondelete="CASCADE"), nullable=True
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("employees.id", ondelete="CASCADE"), nullable=True
    )

    # Listing Details
    source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'anbudstjenester' | 'finn' | 'nummeropplysning' | '1881' | 'gulesider' | 'google' | 'other'
    listing_url: Mapped[str] = mapped_column(Text, nullable=False)
    listing_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="office"
    )  # 'office' | 'broker' | 'company'

    # Verification
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending_check"
    )  # 'verified' | 'needs_update' | 'pending_check' | 'removed'
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    office: Mapped[Optional["Office"]] = relationship(
        "Office", back_populates="external_listings", foreign_keys=[office_id]
    )

    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", back_populates="external_listings", foreign_keys=[employee_id]
    )

    # Indexes
    __table_args__ = (
        Index("idx_external_listings_office_id", "office_id"),
        Index("idx_external_listings_employee_id", "employee_id"),
        Index("idx_external_listings_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ExternalListing(id={self.id}, source='{self.source}', status='{self.status}')>"

    @property
    def is_verified(self) -> bool:
        """Check if listing is verified."""
        return self.status == "verified"

    @property
    def needs_attention(self) -> bool:
        """Check if listing needs attention (update or check)."""
        return self.status in ("needs_update", "pending_check")

    @property
    def source_display_name(self) -> str:
        """Return human-readable source name."""
        names = {
            "anbudstjenester": "Anbudstjenester.no",
            "finn": "Finn.no",
            "nummeropplysning": "Nummeropplysning.no",
            "1881": "1881.no",
            "gulesider": "Gulesider.no",
            "google": "Google Min Bedrift",
            "other": "Annen tjeneste",
        }
        return names.get(self.source, self.source)

    @property
    def owner_type(self) -> str:
        """Return the type of owner (office or employee)."""
        if self.employee_id:
            return "employee"
        elif self.office_id:
            return "office"
        return "unknown"
