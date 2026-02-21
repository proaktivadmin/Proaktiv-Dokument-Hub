"""
Pydantic schemas for the template publishing workflow.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowTransition(BaseModel):
    """Request body for a workflow state transition."""

    action: Literal["submit", "approve", "reject", "unpublish", "archive", "restore"] = Field(
        ..., description="The workflow action to perform"
    )
    reviewer: str | None = Field(None, description="Who is performing the action")
    reason: str | None = Field(None, description="Reason for rejection or other notes")


class WorkflowEvent(BaseModel):
    """A single workflow transition event in the history."""

    timestamp: datetime
    from_status: str
    to_status: str
    actor: str | None = None
    notes: str | None = None


class WorkflowStatusResponse(BaseModel):
    """Response containing the current workflow state of a template."""

    template_id: UUID
    workflow_status: str
    published_version: int | None = None
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    ckeditor_validated: bool = False
    ckeditor_validated_at: datetime | None = None
