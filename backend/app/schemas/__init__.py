"""
Pydantic Schemas for Proaktiv Dokument Hub

V3: Added Office, Employee, CompanyAsset, ExternalListing, Checklist,
    Territory (PostalCode, OfficeTerritory), LayoutPartialVersion, LayoutPartialDefault
"""

from app.schemas.merge_field import (
    MergeFieldBase,
    MergeFieldCreate,
    MergeFieldUpdate,
    MergeFieldResponse,
    MergeFieldListResponse,
    MergeFieldDiscoveryResult,
)
from app.schemas.code_pattern import (
    CodePatternBase,
    CodePatternCreate,
    CodePatternUpdate,
    CodePatternResponse,
    CodePatternListResponse,
)
from app.schemas.layout_partial import (
    LayoutPartialBase,
    LayoutPartialCreate,
    LayoutPartialUpdate,
    LayoutPartialResponse,
    LayoutPartialListResponse,
    LayoutPartialSetDefaultResponse,
)
from app.schemas.template_metadata import (
    TemplateMetadataUpdate,
    TemplateAnalysisResult,
)

# V3 Schemas
from app.schemas.office import (
    OfficeBase,
    OfficeCreate,
    OfficeUpdate,
    OfficeResponse,
    OfficeWithStats,
    OfficeListResponse,
)
from app.schemas.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeWithOffice,
    EmployeeListResponse,
    StartOffboarding,
)
from app.schemas.company_asset import (
    CompanyAssetBase,
    CompanyAssetCreate,
    CompanyAssetUpdate,
    CompanyAssetResponse,
    CompanyAssetListResponse,
    AssetMetadata,
)
from app.schemas.external_listing import (
    ExternalListingBase,
    ExternalListingCreate,
    ExternalListingUpdate,
    ExternalListingResponse,
    ExternalListingListResponse,
    ExternalListingVerify,
)
from app.schemas.checklist import (
    ChecklistItem,
    ChecklistTemplateBase,
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistTemplateResponse,
    ChecklistInstanceBase,
    ChecklistInstanceCreate,
    ChecklistInstanceUpdateProgress,
    ChecklistInstanceResponse,
    ChecklistInstanceWithDetails,
    ChecklistInstanceListResponse,
)
from app.schemas.territory import (
    PostalCodeBase,
    PostalCodeCreate,
    PostalCodeResponse,
    PostalCodeSyncResult,
    OfficeTerritoryBase,
    OfficeTerritoryCreate,
    OfficeTerritoryUpdate,
    OfficeTerritoryResponse,
    OfficeTerritoryWithDetails,
    OfficeTerritoryListResponse,
    TerritoryMapData,
    TerritoryFeature,
    TerritoryImportResult,
    BlacklistEntry,
)
from app.schemas.layout_partial_version import (
    LayoutPartialVersionBase,
    LayoutPartialVersionCreate,
    LayoutPartialVersionResponse,
    LayoutPartialVersionListResponse,
    LayoutPartialRevertRequest,
    LayoutPartialRevertResponse,
    LayoutPartialDefaultBase,
    LayoutPartialDefaultCreate,
    LayoutPartialDefaultUpdate,
    LayoutPartialDefaultResponse,
    LayoutPartialDefaultWithDetails,
    LayoutPartialDefaultListResponse,
)

__all__ = [
    # Merge Field
    "MergeFieldBase",
    "MergeFieldCreate",
    "MergeFieldUpdate",
    "MergeFieldResponse",
    "MergeFieldListResponse",
    "MergeFieldDiscoveryResult",
    # Code Pattern
    "CodePatternBase",
    "CodePatternCreate",
    "CodePatternUpdate",
    "CodePatternResponse",
    "CodePatternListResponse",
    # Layout Partial
    "LayoutPartialBase",
    "LayoutPartialCreate",
    "LayoutPartialUpdate",
    "LayoutPartialResponse",
    "LayoutPartialListResponse",
    "LayoutPartialSetDefaultResponse",
    # Template Metadata
    "TemplateMetadataUpdate",
    "TemplateAnalysisResult",
    # V3: Office
    "OfficeBase",
    "OfficeCreate",
    "OfficeUpdate",
    "OfficeResponse",
    "OfficeWithStats",
    "OfficeListResponse",
    # V3: Employee
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeWithOffice",
    "EmployeeListResponse",
    "StartOffboarding",
    # V3: CompanyAsset
    "CompanyAssetBase",
    "CompanyAssetCreate",
    "CompanyAssetUpdate",
    "CompanyAssetResponse",
    "CompanyAssetListResponse",
    "AssetMetadata",
    # V3: ExternalListing
    "ExternalListingBase",
    "ExternalListingCreate",
    "ExternalListingUpdate",
    "ExternalListingResponse",
    "ExternalListingListResponse",
    "ExternalListingVerify",
    # V3: Checklist
    "ChecklistItem",
    "ChecklistTemplateBase",
    "ChecklistTemplateCreate",
    "ChecklistTemplateUpdate",
    "ChecklistTemplateResponse",
    "ChecklistInstanceBase",
    "ChecklistInstanceCreate",
    "ChecklistInstanceUpdateProgress",
    "ChecklistInstanceResponse",
    "ChecklistInstanceWithDetails",
    "ChecklistInstanceListResponse",
    # V3: Territory
    "PostalCodeBase",
    "PostalCodeCreate",
    "PostalCodeResponse",
    "PostalCodeSyncResult",
    "OfficeTerritoryBase",
    "OfficeTerritoryCreate",
    "OfficeTerritoryUpdate",
    "OfficeTerritoryResponse",
    "OfficeTerritoryWithDetails",
    "OfficeTerritoryListResponse",
    "TerritoryMapData",
    "TerritoryFeature",
    "TerritoryImportResult",
    "BlacklistEntry",
    # V3: Layout Partial Versioning
    "LayoutPartialVersionBase",
    "LayoutPartialVersionCreate",
    "LayoutPartialVersionResponse",
    "LayoutPartialVersionListResponse",
    "LayoutPartialRevertRequest",
    "LayoutPartialRevertResponse",
    "LayoutPartialDefaultBase",
    "LayoutPartialDefaultCreate",
    "LayoutPartialDefaultUpdate",
    "LayoutPartialDefaultResponse",
    "LayoutPartialDefaultWithDetails",
    "LayoutPartialDefaultListResponse",
]
