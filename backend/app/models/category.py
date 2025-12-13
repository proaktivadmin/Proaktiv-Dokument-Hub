"""
Category SQLAlchemy Model
"""

from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.template import Template


class Category(Base):
    """
    Category model for organizing templates.
    
    Categories provide a hierarchical organization structure
    for templates (e.g., "Akseptbrev", "Kontrakter", "AML").
    """
    
    __tablename__ = "categories"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    # Required fields
    name: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False,
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
    
    # Indexes
    __table_args__ = (
        Index("idx_categories_sort_order", "sort_order"),
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', sort_order={self.sort_order})>"

