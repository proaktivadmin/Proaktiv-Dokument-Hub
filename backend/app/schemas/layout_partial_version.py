"""
Pydantic schemas for LayoutPartialVersion and LayoutPartialDefault models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID


# =============================================================================
# Type Aliases
# =============================================================================

DefaultScope = Literal["all", "category", "medium"]
Medium = Literal["pdf", "email", "sms"]


# =============================================================================
# Version Schemas
# =============================================================================

class LayoutPartialVersionBase(BaseModel):
    """Base schema for layout partial versions."""
    html_content: str = Field(..., description="HTML content of this version")
    change_notes: Optional[str] = Field(None, description="Notes about changes in this version")


class LayoutPartialVersionCreate(LayoutPartialVersionBase):
    """Schema for creating a new version."""
    created_by: str = Field(..., description="User who created this version")


class LayoutPartialVersionResponse(LayoutPartialVersionBase):
    """Schema for version responses."""
    id: UUID
    partial_id: UUID
    version_number: int
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LayoutPartialVersionListResponse(BaseModel):
    """Schema for version list."""
    partial_id: UUID
    current_version: int
    versions: List[LayoutPartialVersionResponse]
    
    class Config:
        from_attributes = True


class LayoutPartialRevertRequest(BaseModel):
    """Schema for reverting to a previous version."""
    version_number: int = Field(..., ge=1, description="Version number to revert to")


class LayoutPartialRevertResponse(BaseModel):
    """Schema for revert response."""
    partial_id: UUID
    reverted_from: int
    new_version: int
    message: str


# =============================================================================
# Default Rule Schemas
# =============================================================================

class LayoutPartialDefaultBase(BaseModel):
    """Base schema for default rules."""
    partial_id: UUID = Field(..., description="Layout partial ID")
    scope: DefaultScope = Field("all", description="Scope of the default rule")
    category_id: Optional[UUID] = Field(None, description="Category ID (if scope='category')")
    medium: Optional[Medium] = Field(None, description="Medium (if scope='medium')")
    priority: int = Field(1, ge=1, description="Priority for conflict resolution")


class LayoutPartialDefaultCreate(LayoutPartialDefaultBase):
    """Schema for creating a default rule."""
    pass


class LayoutPartialDefaultUpdate(BaseModel):
    """Schema for updating a default rule."""
    scope: Optional[DefaultScope] = None
    category_id: Optional[UUID] = None
    medium: Optional[Medium] = None
    priority: Optional[int] = Field(None, ge=1)


class CategoryMinimal(BaseModel):
    """Minimal category info for default responses."""
    id: UUID
    name: str
    
    class Config:
        from_attributes = True


class PartialMinimal(BaseModel):
    """Minimal partial info for default responses."""
    id: UUID
    name: str
    type: str
    
    class Config:
        from_attributes = True


class LayoutPartialDefaultResponse(LayoutPartialDefaultBase):
    """Schema for default rule responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    scope_description: str = Field(description="Human-readable scope description")
    
    class Config:
        from_attributes = True


class LayoutPartialDefaultWithDetails(LayoutPartialDefaultResponse):
    """Schema for default rule with related entities."""
    partial: PartialMinimal
    category: Optional[CategoryMinimal] = None
    
    class Config:
        from_attributes = True


class LayoutPartialDefaultListResponse(BaseModel):
    """Schema for default rule list."""
    items: List[LayoutPartialDefaultWithDetails]
    total: int
    
    class Config:
        from_attributes = True
