"""
Tag SQLAlchemy Model
"""

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, TYPE_CHECKING
import uuid

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.template import Template


class Tag(Base):
    """
    Tag model for categorizing templates.
    
    Tags are user-defined labels that can be applied to templates
    for filtering and organization.
    """
    
    __tablename__ = "tags"
    
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
    
    # Optional fields with defaults
    color: Mapped[str] = mapped_column(
        String(7), 
        default="#3B82F6"  # Default blue color
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    templates: Mapped[List["Template"]] = relationship(
        "Template",
        secondary="template_tags",
        back_populates="tags",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', color='{self.color}')>"

