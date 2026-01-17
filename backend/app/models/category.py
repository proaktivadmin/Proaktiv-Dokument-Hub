"""
Category SQLAlchemy Model
"""

from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.template import Template
    from app.models.layout_partial_version import LayoutPartialDefault


class Category(Base):
    """
    Category model for organizing templates.
    
    Categories provide a hierarchical organization structure
    for templates (e.g., "Akseptbrev", "Kontrakter", "AML").
    
    The vitec_id field maps to Vitec Next document category IDs.
    """
    
    __tablename__ = "categories"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Required fields
    name: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Vitec Next category ID (for integration)
    vitec_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        unique=True,
        index=True
    )
    
    # Optional fields
    icon: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True
    )  # Lucide icon name (e.g., "FileText", "Shield")
    
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer, 
        default=0
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    templates: Mapped[List["Template"]] = relationship(
        "Template",
        secondary="template_categories",
        back_populates="categories",
        lazy="selectin"
    )
    
    layout_partial_defaults: Mapped[List["LayoutPartialDefault"]] = relationship(
        "LayoutPartialDefault",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_categories_sort_order", "sort_order"),
        Index("idx_categories_vitec_id", "vitec_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', vitec_id={self.vitec_id})>"

