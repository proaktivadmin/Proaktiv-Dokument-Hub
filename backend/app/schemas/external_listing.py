"""
Pydantic schemas for ExternalListing model.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Type Aliases
# =============================================================================

ListingSource = Literal["anbudstjenester", "finn", "nummeropplysning", "1881", "gulesider", "google", "other"]
ListingType = Literal["office", "broker", "company"]
ListingStatus = Literal["verified", "needs_update", "pending_check", "removed"]


# =============================================================================
# Base Schema
# =============================================================================


class ExternalListingBase(BaseModel):
    """Base schema with common listing fields."""

    office_id: UUID | None = Field(None, description="Office ID (if office listing)")
    employee_id: UUID | None = Field(None, description="Employee ID (if broker listing)")
    source: ListingSource = Field(..., description="Listing source platform")
    listing_url: str = Field(..., description="URL of the external listing")
    listing_type: ListingType = Field("office", description="Type of listing")
    status: ListingStatus = Field("pending_check", description="Verification status")
    notes: str | None = Field(None, description="Internal notes")


# =============================================================================
# Create/Update Schemas
# =============================================================================


class ExternalListingCreate(ExternalListingBase):
    """Schema for creating a new external listing."""

    pass


class ExternalListingUpdate(BaseModel):
    """Schema for updating an external listing."""

    source: ListingSource | None = None
    listing_url: str | None = None
    listing_type: ListingType | None = None
    status: ListingStatus | None = None
    notes: str | None = None


class ExternalListingVerify(BaseModel):
    """Schema for verifying a listing."""

    status: ListingStatus = Field("verified", description="New status after verification")
    notes: str | None = Field(None, description="Verification notes")


# =============================================================================
# Response Schemas
# =============================================================================


class ExternalListingResponse(ExternalListingBase):
    """Schema for external listing responses."""

    id: UUID
    last_verified_at: datetime | None = None
    last_verified_by: str | None = None
    created_at: datetime
    updated_at: datetime

    # Computed properties
    source_display_name: str = Field(description="Human-readable source name")
    owner_type: str = Field(description="Type of owner: office or employee")
    is_verified: bool = Field(description="Whether listing is verified")
    needs_attention: bool = Field(description="Whether listing needs update or check")

    class Config:
        from_attributes = True


class ExternalListingListResponse(BaseModel):
    """Schema for paginated listing list."""

    items: list[ExternalListingResponse]
    total: int

    class Config:
        from_attributes = True
