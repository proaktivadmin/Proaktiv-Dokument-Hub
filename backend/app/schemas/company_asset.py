"""
Pydantic schemas for CompanyAsset model.
"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Type Aliases
# =============================================================================

AssetCategory = Literal["logo", "photo", "marketing", "document", "other"]


# =============================================================================
# Nested Schemas
# =============================================================================


class AssetMetadata(BaseModel):
    """Schema for asset metadata."""

    dimensions: dict[str, int] | None = Field(None, description="Image dimensions {width, height}")
    alt_text: str | None = Field(None, description="Alt text for images")
    usage_notes: str | None = Field(None, description="Notes on how to use this asset")


# =============================================================================
# Base Schema
# =============================================================================


class CompanyAssetBase(BaseModel):
    """Base schema with common asset fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Display name")
    category: AssetCategory = Field("other", description="Asset category")
    office_id: UUID | None = Field(None, description="Office ID for office-scoped assets")
    employee_id: UUID | None = Field(None, description="Employee ID for employee-scoped assets")
    is_global: bool = Field(False, description="Whether asset is company-wide")


# =============================================================================
# Create/Update Schemas
# =============================================================================


class CompanyAssetCreate(CompanyAssetBase):
    """Schema for creating a new asset (file upload handled separately)."""

    metadata: AssetMetadata | None = None


class CompanyAssetUpdate(BaseModel):
    """Schema for updating asset metadata."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: AssetCategory | None = None
    metadata: AssetMetadata | None = None


# =============================================================================
# Response Schemas
# =============================================================================


class CompanyAssetResponse(CompanyAssetBase):
    """Schema for asset responses."""

    id: UUID
    filename: str
    content_type: str
    file_size: int
    storage_path: str
    metadata: dict[str, Any] | None = Field(None, alias="metadata_json")
    created_at: datetime
    updated_at: datetime

    # Computed properties
    scope: str = Field(description="Asset scope: global, office, or employee")
    is_image: bool = Field(description="Whether asset is an image")
    file_size_formatted: str = Field(description="Human-readable file size")

    class Config:
        from_attributes = True
        populate_by_name = True


class CompanyAssetListResponse(BaseModel):
    """Schema for paginated asset list."""

    items: list[CompanyAssetResponse]
    total: int

    class Config:
        from_attributes = True
