"""
CompanyAsset SQLAlchemy Model

Represents file storage scoped to global, office, or employee.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.office import Office


class CompanyAsset(Base):
    """
    CompanyAsset model representing a file stored with ownership scoping.

    Files can be:
    - Global (company-wide, is_global=True)
    - Office-scoped (office_id set)
    - Employee-scoped (employee_id set)
    """

    __tablename__ = "company_assets"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Ownership (one of these defines scope)
    office_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("offices.id", ondelete="CASCADE"), nullable=True
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("employees.id", ondelete="CASCADE"), nullable=True
    )
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # File Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="other"
    )  # 'logo' | 'photo' | 'marketing' | 'document' | 'other'
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)  # WebDAV or blob path

    # Metadata
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONType, nullable=True, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    office: Mapped[Optional["Office"]] = relationship("Office", back_populates="assets", foreign_keys=[office_id])

    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", back_populates="assets", foreign_keys=[employee_id]
    )

    # Indexes
    __table_args__ = (
        Index("idx_company_assets_office_id", "office_id"),
        Index("idx_company_assets_employee_id", "employee_id"),
        Index("idx_company_assets_category", "category"),
        Index("idx_company_assets_is_global", "is_global"),
    )

    def __repr__(self) -> str:
        return f"<CompanyAsset(id={self.id}, name='{self.name}', category='{self.category}')>"

    @property
    def scope(self) -> str:
        """Return the scope type of this asset."""
        if self.is_global:
            return "global"
        elif self.office_id:
            return "office"
        elif self.employee_id:
            return "employee"
        return "unknown"

    @property
    def is_image(self) -> bool:
        """Check if asset is an image based on content type."""
        return self.content_type.startswith("image/")

    @property
    def file_size_formatted(self) -> str:
        """Return human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def alt_text(self) -> str | None:
        """Get alt text from metadata."""
        if self.metadata_json:
            return self.metadata_json.get("alt_text")
        return None

    @property
    def dimensions(self) -> dict[str, int] | None:
        """Get dimensions from metadata for images."""
        if self.metadata_json:
            return self.metadata_json.get("dimensions")
        return None
