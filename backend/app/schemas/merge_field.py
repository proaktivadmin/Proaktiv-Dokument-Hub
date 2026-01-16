"""
Pydantic schemas for Merge Field operations.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MergeFieldBase(BaseModel):
    """Base schema for merge field data."""
    path: str = Field(..., max_length=200, description="Merge field path e.g. eiendom.adresse")
    category: str = Field(..., max_length=100, description="Category e.g. Selger, Eiendom")
    label: str = Field(..., max_length=200, description="Display label")
    description: Optional[str] = Field(None, description="Detailed description")
    example_value: Optional[str] = Field(None, max_length=500, description="Example value")
    data_type: str = Field("string", description="Data type: string, number, date, boolean, array")
    is_iterable: bool = Field(False, description="Can be used with vitec-foreach")
    parent_model: Optional[str] = Field(None, max_length=100, description="Parent model path")


class MergeFieldCreate(MergeFieldBase):
    """Schema for creating a merge field."""
    pass


class MergeFieldUpdate(BaseModel):
    """Schema for updating a merge field (all fields optional)."""
    path: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    label: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    example_value: Optional[str] = Field(None, max_length=500)
    data_type: Optional[str] = None
    is_iterable: Optional[bool] = None
    parent_model: Optional[str] = Field(None, max_length=100)


class MergeFieldResponse(MergeFieldBase):
    """Schema for merge field response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


class MergeFieldListResponse(BaseModel):
    """Schema for paginated merge field list response."""
    merge_fields: List[MergeFieldResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class MergeFieldDiscoveryResult(BaseModel):
    """Schema for merge field auto-discovery result."""
    discovered_count: int
    new_fields: List[str]
    existing_fields: List[str]
    templates_scanned: int
