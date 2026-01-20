"""
Pydantic schemas for Vitec sync review.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from datetime import datetime
from uuid import UUID


class FieldDiff(BaseModel):
    """Field-level diff between local and Vitec values."""

    field_name: str = Field(..., min_length=1)
    local_value: Optional[Any] = Field(None, description="Current local value")
    vitec_value: Optional[Any] = Field(None, description="Incoming Vitec value")
    has_conflict: bool = Field(False, description="Both values exist and differ")
    decision: Optional[Literal["accept", "reject"]] = Field(
        None,
        description="User decision for this field",
    )


class RecordDiff(BaseModel):
    """Diff summary for a single record."""

    match_type: Literal["new", "matched", "not_in_vitec"]
    local_id: Optional[UUID] = None
    vitec_id: Optional[str] = None
    display_name: str
    fields: List[FieldDiff] = Field(default_factory=list)
    match_confidence: float = Field(0.0, ge=0.0, le=1.0)
    match_method: Optional[str] = None


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
    offices: List[RecordDiff] = Field(default_factory=list)
    employees: List[RecordDiff] = Field(default_factory=list)
    summary: SyncSummary
