"""
MergeField SQLAlchemy Model

Represents a Vitec merge field in the Flettekode system.
"""

from sqlalchemy import String, Text, Integer, Boolean, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
import uuid

from app.models.base import Base, GUID


class MergeField(Base):
    """
    Merge field model for the Flettekode system.
    
    Stores registry of Vitec merge fields that can be used in templates.
    Fields are organized by category and can be iterable (for use with vitec-foreach).
    """
    
    __tablename__ = "merge_fields"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Field identification
    path: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Optional metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_value: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Type information
    data_type: Mapped[str] = mapped_column(String(50), default="string")
    is_iterable: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
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
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_merge_fields_category", "category"),
        Index("idx_merge_fields_path", "path"),
        Index("idx_merge_fields_parent_model", "parent_model"),
    )
    
    def __repr__(self) -> str:
        return f"<MergeField(path='{self.path}', category='{self.category}')>"
