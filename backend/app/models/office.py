"""
Office SQLAlchemy Model

Represents a physical office location with contact info and online presence.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.company_asset import CompanyAsset
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
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    
    # Contact
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Address
    street_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Online Presence
    homepage_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    google_my_business_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    facebook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instagram_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Territory Map Color (hex)
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#4A90D9")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
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
    
    # Relationships
    employees: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    assets: Mapped[List["CompanyAsset"]] = relationship(
        "CompanyAsset",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[CompanyAsset.office_id]"
    )
    
    external_listings: Mapped[List["ExternalListing"]] = relationship(
        "ExternalListing",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[ExternalListing.office_id]"
    )
    
    territories: Mapped[List["OfficeTerritory"]] = relationship(
        "OfficeTerritory",
        back_populates="office",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_offices_city", "city"),
        Index("idx_offices_is_active", "is_active"),
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
