"""
Employee SQLAlchemy Model

Represents a company employee with lifecycle management.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.office import Office
    from app.models.company_asset import CompanyAsset
    from app.models.external_listing import ExternalListing
    from app.models.checklist import ChecklistInstance


class Employee(Base):
    """
    Employee model representing a company staff member.
    
    Supports full lifecycle management including onboarding,
    active status, and offboarding with scheduled data deletion.
    """
    
    __tablename__ = "employees"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )

    # Vitec Hub identifiers
    vitec_employee_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Foreign key
    office_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("offices.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Basic Info
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Vitec Next System Roles (e.g., eiendomsmegler, superbruker, daglig_leder)
    system_roles: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list
    )

    
    # Contact
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Online Presence
    homepage_profile_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Profile Content
    profile_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Microsoft 365 Integration
    sharepoint_folder_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    
    # Employment Lifecycle
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="active"
    )  # 'active' | 'onboarding' | 'offboarding' | 'inactive'
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Offboarding Timeline
    hide_from_homepage_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    delete_data_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
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
    office: Mapped["Office"] = relationship(
        "Office",
        back_populates="employees"
    )
    
    assets: Mapped[List["CompanyAsset"]] = relationship(
        "CompanyAsset",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[CompanyAsset.employee_id]"
    )
    
    external_listings: Mapped[List["ExternalListing"]] = relationship(
        "ExternalListing",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[ExternalListing.employee_id]"
    )
    
    checklists: Mapped[List["ChecklistInstance"]] = relationship(
        "ChecklistInstance",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_employees_office_id", "office_id"),
        Index("idx_employees_status", "status"),
        Index("idx_employees_email", "email"),
        Index("idx_employees_vitec_employee_id", "vitec_employee_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, name='{self.full_name}', status='{self.status}')>"
    
    @property
    def full_name(self) -> str:
        """Return formatted full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self) -> str:
        """Return initials for avatar display."""
        first = self.first_name[0].upper() if self.first_name else ""
        last = self.last_name[0].upper() if self.last_name else ""
        return f"{first}{last}"
    
    @property
    def days_until_end(self) -> Optional[int]:
        """Return days until end_date, or None if not set."""
        if not self.end_date:
            return None
        today = date.today()
        delta = self.end_date - today
        return delta.days
    
    @property
    def is_offboarding(self) -> bool:
        """Check if employee is in offboarding status."""
        return self.status == "offboarding"
    
    @property
    def should_hide_from_homepage(self) -> bool:
        """Check if employee should be hidden from homepage."""
        if not self.hide_from_homepage_date:
            return False
        return date.today() >= self.hide_from_homepage_date
    
    def has_role(self, role: str) -> bool:
        """Check if employee has a specific Vitec Next role."""
        if not self.system_roles:
            return False
        return role.lower() in [r.lower() for r in self.system_roles]

