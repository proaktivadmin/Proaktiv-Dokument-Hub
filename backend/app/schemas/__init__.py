"""
Pydantic Schemas for Proaktiv Dokument Hub

V3: Added Office, Employee, CompanyAsset, ExternalListing, Checklist,
    Territory (PostalCode, OfficeTerritory), LayoutPartialVersion, LayoutPartialDefault
"""

from app.schemas.checklist import (
    ChecklistInstanceBase,
    ChecklistInstanceCreate,
    ChecklistInstanceListResponse,
    ChecklistInstanceResponse,
    ChecklistInstanceUpdateProgress,
    ChecklistInstanceWithDetails,
    ChecklistItem,
    ChecklistTemplateBase,
    ChecklistTemplateCreate,
    ChecklistTemplateResponse,
    ChecklistTemplateUpdate,
)
from app.schemas.code_pattern import (
    CodePatternBase,
    CodePatternCreate,
    CodePatternListResponse,
    CodePatternResponse,
    CodePatternUpdate,
)
from app.schemas.company_asset import (
    AssetMetadata,
    CompanyAssetBase,
    CompanyAssetCreate,
    CompanyAssetListResponse,
    CompanyAssetResponse,
    CompanyAssetUpdate,
)
from app.schemas.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeSyncResult,
    EmployeeUpdate,
    EmployeeWithOffice,
    StartOffboarding,
)
from app.schemas.external_listing import (
    ExternalListingBase,
    ExternalListingCreate,
    ExternalListingListResponse,
    ExternalListingResponse,
    ExternalListingUpdate,
    ExternalListingVerify,
)
from app.schemas.firecrawl import (
    FirecrawlScrapeBase,
    FirecrawlScrapeDetail,
    FirecrawlScrapeListResponse,
    FirecrawlScrapeRequest,
)
from app.schemas.layout_partial import (
    LayoutPartialBase,
    LayoutPartialCreate,
    LayoutPartialListResponse,
    LayoutPartialResponse,
    LayoutPartialSetDefaultResponse,
    LayoutPartialUpdate,
)
from app.schemas.layout_partial_version import (
    LayoutPartialDefaultBase,
    LayoutPartialDefaultCreate,
    LayoutPartialDefaultListResponse,
    LayoutPartialDefaultResponse,
    LayoutPartialDefaultUpdate,
    LayoutPartialDefaultWithDetails,
    LayoutPartialRevertRequest,
    LayoutPartialRevertResponse,
    LayoutPartialVersionBase,
    LayoutPartialVersionCreate,
    LayoutPartialVersionListResponse,
    LayoutPartialVersionResponse,
)
from app.schemas.merge_field import (
    MergeFieldBase,
    MergeFieldCreate,
    MergeFieldDiscoveryResult,
    MergeFieldListResponse,
    MergeFieldResponse,
    MergeFieldUpdate,
)

# V3 Schemas
from app.schemas.office import (
    OfficeBase,
    OfficeCreate,
    OfficeListResponse,
    OfficeResponse,
    OfficeSyncResult,
    OfficeUpdate,
    OfficeWithStats,
)
from app.schemas.sync import (
    FieldDiff,
    RecordDiff,
    SyncCommitResult,
    SyncDecisionUpdate,
    SyncPreview,
    SyncSummary,
)
from app.schemas.template_metadata import (
    TemplateAnalysisResult,
    TemplateMetadataUpdate,
)
from app.schemas.territory import (
    BlacklistEntry,
    OfficeTerritoryBase,
    OfficeTerritoryCreate,
    OfficeTerritoryListResponse,
    OfficeTerritoryResponse,
    OfficeTerritoryUpdate,
    OfficeTerritoryWithDetails,
    PostalCodeBase,
    PostalCodeCreate,
    PostalCodeResponse,
    PostalCodeSyncResult,
    TerritoryFeature,
    TerritoryImportResult,
    TerritoryMapData,
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
    "OfficeSyncResult",
    # V3: Employee
    "EmployeeBase",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeWithOffice",
    "EmployeeListResponse",
    "StartOffboarding",
    "EmployeeSyncResult",
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
    # Firecrawl
    "FirecrawlScrapeRequest",
    "FirecrawlScrapeBase",
    "FirecrawlScrapeDetail",
    "FirecrawlScrapeListResponse",
    # Sync Preview
    "FieldDiff",
    "RecordDiff",
    "SyncSummary",
    "SyncPreview",
    "SyncDecisionUpdate",
    "SyncCommitResult",
]
