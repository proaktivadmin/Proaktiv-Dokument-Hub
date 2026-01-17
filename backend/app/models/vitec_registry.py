"""
VitecTemplateRegistry SQLAlchemy Model

Tracks the inventory of Vitec Next templates and their sync status
with the local template library.

Based on the 199 templates from .cursor/vitec-reference.md
"""

from sqlalchemy import String, Text, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import uuid

from app.models.base import Base, GUID


class VitecTemplateRegistry(Base):
    """
    Registry of Vitec Next templates for inventory tracking.
    
    This table tracks:
    - All known Vitec Next templates (from official documentation)
    - Their sync status with the local template library
    - Which local template corresponds to which Vitec template
    
    Sync statuses:
    - synced: Template exists locally and matches Vitec specification
    - missing: Template exists in Vitec but not locally
    - modified: Template exists locally but has been modified
    - local_only: Template exists locally but not in Vitec registry
    """
    
    __tablename__ = "vitec_template_registry"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Vitec template identification
    vitec_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True,
        comment="Official Vitec template name"
    )
    vitec_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Template type: Objekt/Kontakt, System"
    )
    vitec_phase: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="Primary phase: Innsalg, Til salgs, Klargjoring, etc."
    )
    vitec_category: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="Vitec document category"
    )
    vitec_channel: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True,
        comment="Channel: pdf, email, sms"
    )
    
    # Description from Vitec
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Description of the template purpose"
    )
    
    # Sync with local templates
    local_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("templates.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK to local template if synced"
    )
    
    sync_status: Mapped[str] = mapped_column(
        String(20),
        default="missing",
        comment="Status: synced, missing, modified, local_only"
    )
    
    # Tracking
    last_checked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time sync status was checked"
    )
    
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
    local_template = relationship(
        "Template",
        foreign_keys=[local_template_id],
        backref="vitec_registry_entry"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_vitec_registry_name", "vitec_name"),
        Index("idx_vitec_registry_type", "vitec_type"),
        Index("idx_vitec_registry_phase", "vitec_phase"),
        Index("idx_vitec_registry_sync_status", "sync_status"),
        Index("idx_vitec_registry_local_template", "local_template_id"),
    )
    
    def __repr__(self) -> str:
        return f"<VitecTemplateRegistry(name='{self.vitec_name}', status='{self.sync_status}')>"
