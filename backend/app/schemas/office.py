"""
Pydantic schemas for Office model.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Base Schema
# =============================================================================


class OfficeBase(BaseModel):
    """Base schema with common office fields."""

    name: str = Field(..., min_length=1, max_length=200, description="Office marketing/display name")
    legal_name: str | None = Field(None, max_length=200, description="Legal company name (e.g., 'Proaktiv Gruppen AS')")
    short_code: str = Field(..., min_length=1, max_length=10, description="Unique short code (e.g., 'STAV')")
    organization_number: str | None = Field(
        None, max_length=20, description="Norwegian organization number (organisasjonsnummer)"
    )
    vitec_department_id: int | None = Field(None, description="Vitec Hub departmentId")
    email: str | None = Field(None, max_length=255, description="Office email")
    phone: str | None = Field(None, max_length=50, description="Office phone")
    street_address: str | None = Field(None, max_length=255, description="Street address")
    postal_code: str | None = Field(None, max_length=10, description="Postal code")
    city: str | None = Field(None, max_length=100, description="City")
    homepage_url: str | None = Field(None, description="Homepage URL")
    google_my_business_url: str | None = Field(None, description="Google My Business URL")
    facebook_url: str | None = Field(None, description="Facebook page URL")
    instagram_url: str | None = Field(None, description="Instagram profile URL")
    linkedin_url: str | None = Field(None, description="LinkedIn page URL")
    profile_image_url: str | None = Field(None, description="Office profile image URL")
    banner_image_url: str | None = Field(None, description="Office banner image URL for cards")
    description: str | None = Field(None, description="Office description")
    color: str = Field("#4A90D9", pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color for territory map")
    is_active: bool = Field(True, description="Whether office is active")


# =============================================================================
# Create/Update Schemas
# =============================================================================


class OfficeCreate(OfficeBase):
    """Schema for creating a new office."""

    pass


class OfficeUpdate(BaseModel):
    """Schema for updating an office (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=200)
    legal_name: str | None = Field(None, max_length=200)
    short_code: str | None = Field(None, min_length=1, max_length=10)
    organization_number: str | None = Field(None, max_length=20)
    vitec_department_id: int | None = None
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    street_address: str | None = Field(None, max_length=255)
    postal_code: str | None = Field(None, max_length=10)
    city: str | None = Field(None, max_length=100)
    homepage_url: str | None = None
    google_my_business_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    profile_image_url: str | None = None
    banner_image_url: str | None = None
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: bool | None = None


# =============================================================================
# Response Schemas
# =============================================================================


class OfficeResponse(OfficeBase):
    """Schema for office responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfficeWithStats(OfficeResponse):
    """Schema for office with computed statistics."""

    employee_count: int = Field(0, description="Total employees at this office")
    active_employee_count: int = Field(0, description="Active employees at this office")
    territory_count: int = Field(0, description="Number of postal codes covered")

    class Config:
        from_attributes = True


class OfficeListResponse(BaseModel):
    """Schema for paginated office list."""

    items: list[OfficeWithStats]
    total: int

    class Config:
        from_attributes = True


class OfficeSyncResult(BaseModel):
    """Schema for office sync results."""

    total: int
    synced: int
    created: int
    updated: int
    skipped: int
