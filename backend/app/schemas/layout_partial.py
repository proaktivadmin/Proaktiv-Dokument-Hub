"""
Pydantic schemas for Layout Partial operations.

Supports:
- header: Document headers for PDF templates
- footer: Document footers for PDF templates
- signature: Email or SMS signatures
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Type definitions for layout partials
LayoutPartialType = Literal["header", "footer", "signature"]
LayoutPartialContext = Literal["pdf", "email", "sms", "all"]


class LayoutPartialBase(BaseModel):
    """Base schema for layout partial data."""

    name: str = Field(..., max_length=200, description="Partial name")
    type: LayoutPartialType = Field(..., description="Partial type: header, footer, or signature")
    context: LayoutPartialContext = Field("all", description="Usage context: pdf, email, sms, or all")
    html_content: str = Field(..., description="HTML content")
    document_type: str | None = Field(
        None, max_length=50, description="Document type for specialized footers (kontrakt, skjote, etc.)"
    )


class LayoutPartialCreate(LayoutPartialBase):
    """Schema for creating a layout partial."""

    is_default: bool = Field(False, description="Set as default for type/context")


class LayoutPartialUpdate(BaseModel):
    """Schema for updating a layout partial (all fields optional)."""

    name: str | None = Field(None, max_length=200)
    type: LayoutPartialType | None = None
    context: LayoutPartialContext | None = None
    html_content: str | None = None
    document_type: str | None = Field(None, max_length=50)
    is_default: bool | None = None


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

    partials: list[LayoutPartialResponse]
    total: int


class LayoutPartialSetDefaultResponse(BaseModel):
    """Schema for set default operation response."""

    id: UUID
    is_default: bool
    previous_default_id: UUID | None = None
