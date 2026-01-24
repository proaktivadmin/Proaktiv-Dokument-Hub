"""
Office SQLAlchemy Model

Represents a physical office location with contact info and online presence.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base

if TYPE_CHECKING:
    from app.models.company_asset import CompanyAsset
    from app.models.employee import Employee
    from app.models.external_listing import ExternalListing
    from app.models.office_territory import OfficeTerritory


class Office(Base):
    """
    Office model representing a physical office location.

    Stores contact information, address, online presence URLs,
    and territory map color for heatmap visualization.
    """

    __tablename__ = "offices"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    short_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    organization_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vitec_department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Office hierarchy: 'main' (top-level), 'sub' (sub-department), 'regional' (regional grouping)
    office_type: Mapped[str] = mapped_column(String(20), nullable=False, default="main")
    parent_office_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("offices.id", ondelete="SET NULL"), nullable=True
    )

    # Contact
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Address
    street_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Online Presence
    homepage_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    google_my_business_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    facebook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Profile Content
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    banner_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Microsoft 365 Integration
    teams_group_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sharepoint_folder_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Territory Map Color (hex)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#4A90D9")

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", back_populates="office", cascade="all, delete-orphan", lazy="selectin"
    )

    # Parent-child office hierarchy (for sub-departments like Næring, Næringsoppgjør)
    parent_office: Mapped["Office | None"] = relationship(
        "Office",
        back_populates="sub_offices",
        remote_side="Office.id",
        lazy="selectin",
    )
    sub_offices: Mapped[list["Office"]] = relationship(
        "Office",
        back_populates="parent_office",
        lazy="selectin",
    )

    assets: Mapped[list["CompanyAsset"]] = relationship(
        "CompanyAsset",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[CompanyAsset.office_id]",
    )

    external_listings: Mapped[list["ExternalListing"]] = relationship(
        "ExternalListing",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[ExternalListing.office_id]",
    )

    territories: Mapped[list["OfficeTerritory"]] = relationship(
        "OfficeTerritory", back_populates="office", cascade="all, delete-orphan", lazy="selectin"
    )

    # Indexes
    __table_args__ = (
        Index("idx_offices_city", "city"),
        Index("idx_offices_is_active", "is_active"),
        Index("idx_offices_vitec_department_id", "vitec_department_id"),
        Index("idx_offices_organization_number", "organization_number"),
        Index("idx_offices_parent_office_id", "parent_office_id"),
        Index("idx_offices_office_type", "office_type"),
    )

    def __repr__(self) -> str:
        return f"<Office(id={self.id}, name='{self.name}', short_code='{self.short_code}')>"

    @property
    def full_address(self) -> str:
        """Return formatted full address."""
        parts = []
        if self.street_address:
            parts.append(self.street_address)
        if self.postal_code and self.city:
            parts.append(f"{self.postal_code} {self.city}")
        elif self.city:
            parts.append(self.city)
        return ", ".join(parts)

    @property
    def employee_count(self) -> int:
        """Return count of employees."""
        return len(self.employees) if self.employees else 0

    @property
    def active_employee_count(self) -> int:
        """Return count of active employees."""
        if not self.employees:
            return 0
        return len([e for e in self.employees if e.status == "active"])

    @property
    def is_main_office(self) -> bool:
        """Check if this is a main (top-level) office."""
        return self.office_type == "main"

    @property
    def is_sub_office(self) -> bool:
        """Check if this is a sub-department."""
        return self.office_type == "sub"

    @property
    def has_sub_offices(self) -> bool:
        """Check if this office has sub-departments."""
        return bool(self.sub_offices)
