"""
Pydantic schemas for Merge Field operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MergeFieldBase(BaseModel):
    """Base schema for merge field data."""

    path: str = Field(..., max_length=200, description="Merge field path e.g. eiendom.adresse")
    category: str = Field(..., max_length=100, description="Category e.g. Selger, Eiendom")
    label: str = Field(..., max_length=200, description="Display label")
    description: str | None = Field(None, description="Detailed description")
    example_value: str | None = Field(None, max_length=500, description="Example value")
    data_type: str = Field("string", description="Data type: string, number, date, boolean, array")
    is_iterable: bool = Field(False, description="Can be used with vitec-foreach")
    parent_model: str | None = Field(None, max_length=100, description="Parent model path")


class MergeFieldCreate(MergeFieldBase):
    """Schema for creating a merge field."""

    pass


class MergeFieldUpdate(BaseModel):
    """Schema for updating a merge field (all fields optional)."""

    path: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=100)
    label: str | None = Field(None, max_length=200)
    description: str | None = None
    example_value: str | None = Field(None, max_length=500)
    data_type: str | None = None
    is_iterable: bool | None = None
    parent_model: str | None = Field(None, max_length=100)


class MergeFieldResponse(MergeFieldBase):
    """Schema for merge field response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


class MergeFieldListResponse(BaseModel):
    """Schema for paginated merge field list response."""

    merge_fields: list[MergeFieldResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class MergeFieldDiscoveryResult(BaseModel):
    """Schema for merge field auto-discovery result."""

    discovered_count: int
    new_fields: list[str]
    existing_fields: list[str]
    templates_scanned: int
