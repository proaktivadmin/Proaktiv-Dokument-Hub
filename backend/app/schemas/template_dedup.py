"""
Pydantic schemas for template deduplication and merge analysis.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MergeCandidate(BaseModel):
    """A single template that is part of a merge candidate group."""

    template_id: UUID
    title: str
    property_type: str | None = None
    content_length: int = 0
    similarity_score: float = Field(0.0, ge=0.0, le=1.0, description="Similarity to the group primary (0-1)")


class MergeCandidateGroup(BaseModel):
    """A group of templates that serve the same purpose and could be merged."""

    base_title: str
    candidates: list[MergeCandidate]
    category: str | None = None
    estimated_reduction: int = Field(0, description="How many templates would be eliminated by merging")


class ContentSection(BaseModel):
    """A section of template content identified during analysis."""

    path: str = Field(..., description="CSS selector path to section")
    content_hash: str
    is_shared: bool
    differs_in: list[str] = Field(default_factory=list, description="Template IDs where this section differs")
    preview: str = Field("", description="First 100 chars of section content")


class MergeAnalysis(BaseModel):
    """Result of deep-comparing a group of templates for merge potential."""

    group_title: str
    templates: list[MergeCandidate]
    shared_sections: list[ContentSection] = Field(default_factory=list)
    divergent_sections: list[ContentSection] = Field(default_factory=list)
    unique_sections: list[ContentSection] = Field(default_factory=list)
    merge_complexity: Literal["simple", "moderate", "complex"] = "moderate"
    auto_mergeable: bool = Field(False, description="True if differences are only property-type text")
    warnings: list[str] = Field(default_factory=list)


class MergePreview(BaseModel):
    """Preview of a merged template before committing."""

    merged_html: str
    primary_template_id: UUID
    templates_to_archive: list[UUID] = Field(default_factory=list)
    vitec_if_conditions_added: int = 0
    warnings: list[str] = Field(default_factory=list)
    validation_passed: bool = False


class MergeResult(BaseModel):
    """Result of executing a merge operation."""

    primary_template_id: UUID
    archived_template_ids: list[UUID] = Field(default_factory=list)
    new_version: int = 1
    property_types_covered: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    """Request body for analyzing a group of templates."""

    template_ids: list[UUID] = Field(..., min_length=2)


class PreviewRequest(BaseModel):
    """Request body for previewing a merge."""

    template_ids: list[UUID] = Field(..., min_length=2)
    primary_id: UUID


class ExecuteRequest(BaseModel):
    """Request body for executing a merge."""

    template_ids: list[UUID] = Field(..., min_length=2)
    primary_id: UUID
    merged_html: str
