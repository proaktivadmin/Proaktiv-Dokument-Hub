"""
Pydantic schemas for Layout Partial operations.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime


class LayoutPartialBase(BaseModel):
    """Base schema for layout partial data."""
    name: str = Field(..., max_length=200, description="Partial name")
    type: Literal['header', 'footer'] = Field(..., description="Partial type")
    context: Literal['pdf', 'email', 'all'] = Field('all', description="Usage context")
    html_content: str = Field(..., description="HTML content")


class LayoutPartialCreate(LayoutPartialBase):
    """Schema for creating a layout partial."""
    is_default: bool = Field(False, description="Set as default for type/context")


class LayoutPartialUpdate(BaseModel):
    """Schema for updating a layout partial (all fields optional)."""
    name: Optional[str] = Field(None, max_length=200)
    type: Optional[Literal['header', 'footer']] = None
    context: Optional[Literal['pdf', 'email', 'all']] = None
    html_content: Optional[str] = None
    is_default: Optional[bool] = None


class LayoutPartialResponse(LayoutPartialBase):
    """Schema for layout partial response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    is_default: bool
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class LayoutPartialListResponse(BaseModel):
    """Schema for paginated layout partial list response."""
    partials: List[LayoutPartialResponse]
    total: int


class LayoutPartialSetDefaultResponse(BaseModel):
    """Schema for set default operation response."""
    id: UUID
    is_default: bool
    previous_default_id: Optional[UUID] = None
