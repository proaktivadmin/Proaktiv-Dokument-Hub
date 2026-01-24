"""
Pydantic schemas for Notification model.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Type Aliases
# =============================================================================

NotificationType = Literal[
    "employee_added",
    "employee_removed",
    "employee_updated",
    "office_added",
    "office_removed",
    "office_updated",
    "upn_mismatch",
    "sync_error",
]

NotificationSeverity = Literal["info", "warning", "error"]
NotificationEntityType = Literal["employee", "office", "sync"]


# =============================================================================
# Base Schema
# =============================================================================


class NotificationBase(BaseModel):
    """Base schema with common notification fields."""

    type: NotificationType = Field(..., description="Notification type")
    entity_type: NotificationEntityType = Field(..., description="Related entity type")
    entity_id: UUID | None = Field(None, description="Related entity ID")
    title: str = Field(..., max_length=255, description="Short notification title")
    message: str = Field(..., description="Detailed notification message")
    severity: NotificationSeverity = Field("info", description="Severity level")
    metadata: dict[str, object] | None = Field(None, description="Optional structured metadata")


# =============================================================================
# Create Schema
# =============================================================================


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    pass


# =============================================================================
# Response Schemas
# =============================================================================


class NotificationResponse(NotificationBase):
    """Schema for notification responses."""

    id: UUID
    is_read: bool
    created_at: datetime
    metadata: dict[str, object] | None = Field(None, alias="metadata_json")

    class Config:
        from_attributes = True
        populate_by_name = True


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    items: list[NotificationResponse]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count."""

    count: int
