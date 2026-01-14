"""
CodePattern SQLAlchemy Model

Represents reusable HTML/Vitec code snippets for template building.
"""

from sqlalchemy import String, Text, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional, List
import uuid

from app.models.base import Base


class CodePattern(Base):
    """
    Code pattern model for reusable HTML/Vitec snippets.
    
    Stores pre-built code patterns that can be inserted into templates.
    Patterns are organized by category and track which merge fields they use.
    """
    
    __tablename__ = "code_patterns"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Pattern identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Content
    html_code: Mapped[str] = mapped_column(Text, nullable=False)
    variables_used: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list
    )
    
    # Preview
    preview_thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Audit fields
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
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
        Index("idx_code_patterns_category", "category"),
        Index("idx_code_patterns_name", "name"),
    )
    
    def __repr__(self) -> str:
        return f"<CodePattern(name='{self.name}', category='{self.category}')>"
