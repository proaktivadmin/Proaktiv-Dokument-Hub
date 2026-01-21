"""
Pydantic schemas for Code Pattern operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CodePatternBase(BaseModel):
    """Base schema for code pattern data."""

    name: str = Field(..., max_length=200, description="Pattern name")
    category: str = Field(..., max_length=100, description="Category e.g. Tabeller, Betingelser")
    description: str | None = Field(None, description="Description of the pattern")
    html_code: str = Field(..., description="HTML/Vitec code content")
    variables_used: list[str] = Field(default_factory=list, description="List of merge field paths used")


class CodePatternCreate(CodePatternBase):
    """Schema for creating a code pattern."""

    pass


class CodePatternUpdate(BaseModel):
    """Schema for updating a code pattern (all fields optional)."""

    name: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=100)
    description: str | None = None
    html_code: str | None = None
    variables_used: list[str] | None = None


class CodePatternResponse(CodePatternBase):
    """Schema for code pattern response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    preview_thumbnail_url: str | None = None
    usage_count: int = 0
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class CodePatternListResponse(BaseModel):
    """Schema for paginated code pattern list response."""

    patterns: list[CodePatternResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
