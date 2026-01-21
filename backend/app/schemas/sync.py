"""
Pydantic schemas for Vitec sync review.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class FieldDiff(BaseModel):
    """Field-level diff between local and Vitec values."""

    field_name: str = Field(..., min_length=1)
    local_value: Any | None = Field(None, description="Current local value")
    vitec_value: Any | None = Field(None, description="Incoming Vitec value")
    has_conflict: bool = Field(False, description="Both values exist and differ")
    decision: Literal["accept", "reject"] | None = Field(
        None,
        description="User decision for this field",
    )


class RecordDiff(BaseModel):
    """Diff summary for a single record."""

    match_type: Literal["new", "matched", "not_in_vitec"]
    local_id: UUID | None = None
    vitec_id: str | None = None
    display_name: str
    fields: list[FieldDiff] = Field(default_factory=list)
    match_confidence: float = Field(0.0, ge=0.0, le=1.0)
    match_method: str | None = None


class SyncSummary(BaseModel):
    """Summary counts for sync preview."""

    offices_new: int = 0
    offices_matched: int = 0
    offices_not_in_vitec: int = 0
    employees_new: int = 0
    employees_matched: int = 0
    employees_not_in_vitec: int = 0
    employees_missing_office: int = 0


class SyncPreview(BaseModel):
    """Full preview response for a sync session."""

    session_id: UUID
    created_at: datetime
    expires_at: datetime
    offices: list[RecordDiff] = Field(default_factory=list)
    employees: list[RecordDiff] = Field(default_factory=list)
    summary: SyncSummary


class SyncDecisionUpdate(BaseModel):
    """Update decision for a single field."""

    record_type: Literal["office", "employee"]
    record_id: str = Field(..., min_length=1)
    field_name: str = Field(..., min_length=1)
    decision: Literal["accept", "reject"]


class SyncCommitResult(BaseModel):
    """Summary of applied changes after commit."""

    offices_created: int = 0
    offices_updated: int = 0
    offices_skipped: int = 0
    employees_created: int = 0
    employees_updated: int = 0
    employees_skipped: int = 0
