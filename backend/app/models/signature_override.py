"""
Signature Override SQLAlchemy Model

Stores employee-provided overrides for their email signature fields.
All fields are nullable — null means "use original synced value."
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class SignatureOverride(Base):
    """
    Per-employee signature field overrides.

    Employees can customize their signature fields via the public
    signature page. These overrides are stored separately from the
    synced Vitec/Entra data so the original dataset is never modified.
    """

    __tablename__ = "signature_overrides"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(
        GUID,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Contact overrides (null = use original)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mobile_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    office_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Social URL overrides (null = use default resolution)
    facebook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    employee_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    employee: Mapped["Employee"] = relationship("Employee", back_populates="signature_override")
