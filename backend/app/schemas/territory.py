"""
Pydantic schemas for PostalCode and OfficeTerritory models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, date
from uuid import UUID


# =============================================================================
# Type Aliases
# =============================================================================

TerritorySource = Literal["vitec_next", "finn", "anbudstjenester", "homepage", "other"]


# =============================================================================
# PostalCode Schemas
# =============================================================================

class PostalCodeBase(BaseModel):
    """Base schema for postal codes."""
    postal_code: str = Field(..., min_length=4, max_length=10, description="Postal code")
    postal_name: str = Field(..., min_length=1, max_length=100, description="Postal name")
    municipality_code: Optional[str] = Field(None, max_length=10, description="Municipality code")
    municipality_name: Optional[str] = Field(None, max_length=100, description="Municipality name")
    category: Optional[str] = Field(None, max_length=10, description="Category (G, B, F, P, S)")


class PostalCodeCreate(PostalCodeBase):
    """Schema for creating a postal code."""
    pass


class PostalCodeResponse(PostalCodeBase):
    """Schema for postal code responses."""
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    full_location: str = Field(description="Formatted location string")
    category_name: str = Field(description="Human-readable category name")
    is_street_address: bool = Field(description="Whether postal code is for street addresses")
    
    class Config:
        from_attributes = True


class PostalCodeSyncResult(BaseModel):
    """Schema for postal code sync results."""
    synced: int = Field(description="Number of postal codes synced")
    message: str = Field(description="Result message")


# =============================================================================
# OfficeTerritory Schemas
# =============================================================================

class OfficeTerritoryBase(BaseModel):
    """Base schema for office territories."""
    office_id: UUID = Field(..., description="Office ID")
    postal_code: str = Field(..., min_length=4, max_length=10, description="Postal code")
    source: TerritorySource = Field("vitec_next", description="Territory source")
    priority: int = Field(1, ge=1, description="Priority (higher overrides lower)")
    is_blacklisted: bool = Field(False, description="Whether area is blacklisted")
    valid_from: Optional[date] = Field(None, description="Start of validity period")
    valid_to: Optional[date] = Field(None, description="End of validity period")


class OfficeTerritoryCreate(OfficeTerritoryBase):
    """Schema for creating a territory assignment."""
    pass


class OfficeTerritoryUpdate(BaseModel):
    """Schema for updating a territory assignment."""
    source: Optional[TerritorySource] = None
    priority: Optional[int] = Field(None, ge=1)
    is_blacklisted: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class OfficeMinimalForTerritory(BaseModel):
    """Minimal office info for territory responses."""
    id: UUID
    name: str
    short_code: str
    color: str
    
    class Config:
        from_attributes = True


class OfficeTerritoryResponse(OfficeTerritoryBase):
    """Schema for territory responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: bool = Field(description="Whether territory is currently active")
    source_display_name: str = Field(description="Human-readable source name")
    
    class Config:
        from_attributes = True


class OfficeTerritoryWithDetails(OfficeTerritoryResponse):
    """Schema for territory with office and postal code details."""
    office: OfficeMinimalForTerritory
    postal_info: PostalCodeResponse
    
    class Config:
        from_attributes = True


class OfficeTerritoryListResponse(BaseModel):
    """Schema for paginated territory list."""
    items: List[OfficeTerritoryWithDetails]
    total: int
    
    class Config:
        from_attributes = True


# =============================================================================
# GeoJSON Schemas for Map
# =============================================================================

class TerritoryFeatureProperties(BaseModel):
    """Properties for a territory map feature."""
    postal_code: str
    postal_name: str
    office_id: Optional[str] = None
    office_name: Optional[str] = None
    office_color: Optional[str] = None
    source: Optional[TerritorySource] = None
    is_blacklisted: bool = False


class TerritoryFeature(BaseModel):
    """GeoJSON Feature for a territory."""
    type: Literal["Feature"] = "Feature"
    properties: TerritoryFeatureProperties
    geometry: Dict[str, Any]  # GeoJSON Polygon


class TerritoryMapData(BaseModel):
    """GeoJSON FeatureCollection for the territory map."""
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[TerritoryFeature]


# =============================================================================
# Import Schemas
# =============================================================================

class TerritoryImportResult(BaseModel):
    """Schema for territory import results."""
    imported: int = Field(description="Number of territories imported")
    errors: List[str] = Field(default_factory=list, description="Import errors")


class BlacklistEntry(BaseModel):
    """Schema for adding to blacklist."""
    postal_code: str = Field(..., min_length=4, max_length=10, description="Postal code to blacklist")
