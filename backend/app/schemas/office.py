"""
Pydantic schemas for Office model.
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# =============================================================================
# Base Schema
# =============================================================================

class OfficeBase(BaseModel):
    """Base schema with common office fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Office marketing/display name")
    legal_name: Optional[str] = Field(None, max_length=200, description="Legal company name (e.g., 'Proaktiv Gruppen AS')")
    short_code: str = Field(..., min_length=1, max_length=10, description="Unique short code (e.g., 'STAV')")
    organization_number: Optional[str] = Field(None, max_length=20, description="Norwegian organization number (organisasjonsnummer)")
    vitec_department_id: Optional[int] = Field(None, description="Vitec Hub departmentId")
    email: Optional[str] = Field(None, max_length=255, description="Office email")
    phone: Optional[str] = Field(None, max_length=50, description="Office phone")
    street_address: Optional[str] = Field(None, max_length=255, description="Street address")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    city: Optional[str] = Field(None, max_length=100, description="City")
    homepage_url: Optional[str] = Field(None, description="Homepage URL")
    google_my_business_url: Optional[str] = Field(None, description="Google My Business URL")
    facebook_url: Optional[str] = Field(None, description="Facebook page URL")
    instagram_url: Optional[str] = Field(None, description="Instagram profile URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn page URL")
    profile_image_url: Optional[str] = Field(None, description="Office profile image URL")
    banner_image_url: Optional[str] = Field(None, description="Office banner image URL for cards")
    description: Optional[str] = Field(None, description="Office description")
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
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    short_code: Optional[str] = Field(None, min_length=1, max_length=10)
    organization_number: Optional[str] = Field(None, max_length=20)
    vitec_department_id: Optional[int] = None
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    street_address: Optional[str] = Field(None, max_length=255)
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    homepage_url: Optional[str] = None
    google_my_business_url: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None


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
    items: List[OfficeWithStats]
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
