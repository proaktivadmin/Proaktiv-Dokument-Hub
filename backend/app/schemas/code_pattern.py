"""
Pydantic schemas for Code Pattern operations.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CodePatternBase(BaseModel):
    """Base schema for code pattern data."""
    name: str = Field(..., max_length=200, description="Pattern name")
    category: str = Field(..., max_length=100, description="Category e.g. Tabeller, Betingelser")
    description: Optional[str] = Field(None, description="Description of the pattern")
    html_code: str = Field(..., description="HTML/Vitec code content")
    variables_used: List[str] = Field(default_factory=list, description="List of merge field paths used")


class CodePatternCreate(CodePatternBase):
    """Schema for creating a code pattern."""
    pass


class CodePatternUpdate(BaseModel):
    """Schema for updating a code pattern (all fields optional)."""
    name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    html_code: Optional[str] = None
    variables_used: Optional[List[str]] = None


class CodePatternResponse(CodePatternBase):
    """Schema for code pattern response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    preview_thumbnail_url: Optional[str] = None
    usage_count: int = 0
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class CodePatternListResponse(BaseModel):
    """Schema for paginated code pattern list response."""
    patterns: List[CodePatternResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
