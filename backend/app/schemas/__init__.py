"""
Pydantic Schemas for Proaktiv Dokument Hub
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
]
