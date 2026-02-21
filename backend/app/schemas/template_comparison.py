"""
Pydantic schemas for AI-powered template comparison and change analysis.
"""

from typing import Literal

from pydantic import BaseModel, Field


class StructuralChange(BaseModel):
    """A single structural change detected between two HTML templates."""

    category: Literal["cosmetic", "structural", "content", "merge_fields", "logic", "breaking"] = Field(
        ..., description="Classification of the change"
    )
    element_path: str = Field(..., description="CSS-like path to the changed element")
    description: str = Field(..., description="Human-readable description of the change")
    before: str | None = Field(None, description="Content before the change (truncated)")
    after: str | None = Field(None, description="Content after the change (truncated)")


class Conflict(BaseModel):
    """A conflict where both our customization and Vitec's update touch the same section."""

    section: str = Field(..., description="Human-readable section description")
    our_change: str = Field(..., description="What we modified")
    vitec_change: str = Field(..., description="What Vitec modified")
    severity: Literal["low", "medium", "high"] = Field(..., description="Conflict severity")


class ChangeClassification(BaseModel):
    """Aggregate counts of changes by category."""

    cosmetic: int = 0
    structural: int = 0
    content: int = 0
    merge_fields: int = 0
    logic: int = 0
    breaking: int = 0
    total: int = 0


class ComparisonResult(BaseModel):
    """Result of structural HTML comparison between two templates."""

    changes: list[StructuralChange] = Field(default_factory=list)
    classification: ChangeClassification = Field(default_factory=ChangeClassification)
    conflicts: list[Conflict] = Field(default_factory=list)
    stored_hash: str = Field(..., description="SHA256 hash of the stored template")
    updated_hash: str = Field(..., description="SHA256 hash of the updated template")
    hashes_match: bool = Field(..., description="Whether the two templates are identical")


class AnalysisReport(BaseModel):
    """Complete analysis report combining structural diff and AI interpretation."""

    summary: str = Field(..., description="2-3 sentence high-level summary")
    changes_by_category: dict[str, list[str]] = Field(
        default_factory=dict, description="Changes grouped by category, each as plain-language bullets"
    )
    impact: str = Field(..., description="What the changes mean for our customized copy")
    conflicts: list[Conflict] = Field(default_factory=list)
    recommendation: Literal["ADOPT", "IGNORE", "PARTIAL_MERGE", "REVIEW_REQUIRED"] = Field(
        ..., description="Recommended action"
    )
    suggested_actions: list[str] = Field(default_factory=list, description="Specific steps if PARTIAL_MERGE")
    ai_powered: bool = Field(..., description="False if LLM was unavailable and only structural diff was returned")
    raw_comparison: ComparisonResult


class CompareRequest(BaseModel):
    """Request body for comparing a stored template against updated Vitec source."""

    updated_html: str = Field(..., description="The pasted updated Vitec source HTML")


class CompareStandaloneRequest(BaseModel):
    """Request body for ad-hoc comparison of two arbitrary HTML strings."""

    stored_html: str = Field(..., description="The original/stored HTML")
    updated_html: str = Field(..., description="The updated HTML to compare against")
    template_title: str = Field(..., description="Title for context in the analysis")


class CompareApplyRequest(BaseModel):
    """Request body for applying a comparison decision."""

    action: Literal["adopt", "ignore", "partial"] = Field(..., description="Action to take")
    sections_to_adopt: list[str] | None = Field(None, description="For partial merge (future)")
    updated_html: str | None = Field(None, description="The updated Vitec HTML (needed for adopt)")
