"""
Checklist SQLAlchemy Models

ChecklistTemplate: Defines a reusable checklist structure
ChecklistInstance: An assigned checklist for a specific employee
"""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType

if TYPE_CHECKING:
    from app.models.employee import Employee


class ChecklistTemplate(Base):
    """
    ChecklistTemplate model representing a reusable checklist structure.

    Used for onboarding and offboarding processes with a list of items.
    """

    __tablename__ = "checklist_templates"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'onboarding' | 'offboarding'

    # Items - JSONB array of {name, description, required, order}
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, nullable=False, default=list)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    instances: Mapped[list["ChecklistInstance"]] = relationship(
        "ChecklistInstance", back_populates="template", cascade="all, delete-orphan", lazy="selectin"
    )

    # Indexes
    __table_args__ = (Index("idx_checklist_templates_type", "type"),)

    def __repr__(self) -> str:
        return f"<ChecklistTemplate(id={self.id}, name='{self.name}', type='{self.type}')>"

    @property
    def item_count(self) -> int:
        """Return total number of items."""
        return len(self.items) if self.items else 0

    @property
    def required_item_count(self) -> int:
        """Return number of required items."""
        if not self.items:
            return 0
        return len([i for i in self.items if i.get("required", False)])

    def get_item_names(self) -> list[str]:
        """Return list of item names in order."""
        if not self.items:
            return []
        sorted_items = sorted(self.items, key=lambda x: x.get("order", 0))
        return [i.get("name", "") for i in sorted_items]


class ChecklistInstance(Base):
    """
    ChecklistInstance model representing an assigned checklist for an employee.

    Tracks completion progress of each item in the template.
    """

    __tablename__ = "checklist_instances"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    template_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("checklist_templates.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_progress"
    )  # 'in_progress' | 'completed' | 'cancelled'

    # Items completed - JSONB array of item names
    items_completed: Mapped[list[str]] = mapped_column(JSONType, nullable=False, default=list)

    # Dates
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    template: Mapped["ChecklistTemplate"] = relationship("ChecklistTemplate", back_populates="instances")

    employee: Mapped["Employee"] = relationship("Employee", back_populates="checklists")

    # Indexes
    __table_args__ = (
        Index("idx_checklist_instances_employee_id", "employee_id"),
        Index("idx_checklist_instances_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ChecklistInstance(id={self.id}, status='{self.status}')>"

    @property
    def completed_count(self) -> int:
        """Return number of completed items."""
        return len(self.items_completed) if self.items_completed else 0

    @property
    def total_count(self) -> int:
        """Return total number of items from template."""
        if self.template:
            return self.template.item_count
        return 0

    @property
    def progress_percentage(self) -> int:
        """Return completion percentage (0-100)."""
        total = self.total_count
        if total == 0:
            return 0
        return int((self.completed_count / total) * 100)

    @property
    def is_completed(self) -> bool:
        """Check if checklist is completed."""
        return self.status == "completed"

    @property
    def is_overdue(self) -> bool:
        """Check if checklist is overdue."""
        if not self.due_date or self.is_completed:
            return False
        return date.today() > self.due_date

    def mark_item_completed(self, item_name: str) -> bool:
        """Mark an item as completed. Returns True if added, False if already exists."""
        if not self.items_completed:
            self.items_completed = []
        if item_name not in self.items_completed:
            self.items_completed.append(item_name)
            return True
        return False

    def mark_item_incomplete(self, item_name: str) -> bool:
        """Mark an item as incomplete. Returns True if removed, False if not found."""
        if not self.items_completed:
            return False
        if item_name in self.items_completed:
            self.items_completed.remove(item_name)
            return True
        return False
