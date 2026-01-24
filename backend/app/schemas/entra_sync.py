"""
Pydantic schemas for Entra ID sync operations.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Type Aliases
# =============================================================================

SyncScope = Literal["profile", "photo", "signature"]


# =============================================================================
# Property Change Schema
# =============================================================================


class PropertyChange(BaseModel):
    """Represents a single property change between local DB and Entra ID."""

    property: str = Field(..., description="Property name (e.g., 'jobTitle', 'mobilePhone')")
    current_value: str | None = Field(None, description="Current value in Entra ID")
    new_value: str | None = Field(None, description="New value from local database")
    will_update: bool = Field(..., description="Whether this property will be updated")


# =============================================================================
# Preview Schemas
# =============================================================================


class EntraSyncPreview(BaseModel):
    """Preview of what would change for an employee when syncing to Entra ID."""

    employee_id: UUID = Field(..., description="Employee UUID from local database")
    employee_name: str = Field(..., description="Employee full name")
    employee_email: str | None = Field(None, description="Employee email address")
    entra_user_found: bool = Field(..., description="Whether the user was found in Entra ID")
    entra_user_id: str | None = Field(None, description="Entra ID user object ID (GUID)")
    entra_upn: str | None = Field(None, description="Entra ID user principal name")
    profile_changes: list[PropertyChange] = Field(default_factory=list, description="List of profile property changes")
    photo_needs_update: bool = Field(False, description="Whether the profile photo needs updating")
    photo_url: str | None = Field(None, description="Profile photo URL from database")
    signature_preview_available: bool = Field(True, description="Whether signature preview is available")


class SignaturePreview(BaseModel):
    """Preview of the email signature for an employee."""

    employee_id: UUID = Field(..., description="Employee UUID")
    employee_name: str = Field(..., description="Employee full name")
    html: str = Field(..., description="HTML signature content")
    text: str = Field(..., description="Plain text signature content")


# =============================================================================
# Sync Request Schemas
# =============================================================================


class EntraImportRequest(BaseModel):
    """Request to import Entra ID users into local database (read-only to Entra)."""

    dry_run: bool = Field(False, description="Preview changes without updating database")
    filter_email: str | None = Field(None, description="Only update a specific employee email")


class EntraSyncRequest(BaseModel):
    """Request to sync a single employee to Entra ID."""

    scope: list[SyncScope] = Field(
        default=["profile", "photo", "signature"],
        description="What to sync: profile, photo, signature",
    )
    dry_run: bool = Field(False, description="Preview changes without applying")


class EntraSyncBatchRequest(BaseModel):
    """Request to sync multiple employees to Entra ID."""

    employee_ids: list[UUID] = Field(..., min_length=1, description="List of employee UUIDs to sync")
    scope: list[SyncScope] = Field(
        default=["profile", "photo", "signature"],
        description="What to sync: profile, photo, signature",
    )
    dry_run: bool = Field(False, description="Preview changes without applying")


# =============================================================================
# Sync Result Schemas
# =============================================================================


class EntraImportResult(BaseModel):
    """Result of importing Entra ID users into local database."""

    success: bool = Field(..., description="Whether the import completed successfully")
    dry_run: bool = Field(False, description="Whether this was a dry run")
    employees_loaded: int | None = Field(None, description="Employees loaded from database")
    matched_updated: int | None = Field(None, description="Employees matched and updated")
    employees_not_matched: int | None = Field(None, description="Employees without Entra match")
    entra_users_not_matched: int | None = Field(None, description="Entra users without employee match")
    error: str | None = Field(None, description="Error message if import failed")


class EntraSyncResult(BaseModel):
    """Result of syncing a single employee to Entra ID."""

    success: bool = Field(..., description="Whether the overall sync was successful")
    employee_id: UUID = Field(..., description="Employee UUID")
    employee_name: str = Field(..., description="Employee full name")
    entra_user_id: str | None = Field(None, description="Entra ID user object ID")

    # Per-component results
    profile_updated: bool = Field(False, description="Whether profile was updated")
    profile_changes: list[str] = Field(default_factory=list, description="List of changed properties")
    profile_error: str | None = Field(None, description="Profile sync error message")

    photo_updated: bool = Field(False, description="Whether photo was uploaded")
    photo_error: str | None = Field(None, description="Photo sync error message")

    signature_pushed: bool = Field(False, description="Whether signature was pushed")
    signature_error: str | None = Field(None, description="Signature sync error message")

    error: str | None = Field(None, description="General error message")


class EntraSyncBatchResult(BaseModel):
    """Result of syncing multiple employees to Entra ID."""

    total: int = Field(..., description="Total number of employees requested")
    successful: int = Field(..., description="Number of successfully synced employees")
    failed: int = Field(..., description="Number of failed syncs")
    skipped: int = Field(..., description="Number of skipped employees (not found in Entra)")

    results: list[EntraSyncResult] = Field(default_factory=list, description="Individual sync results")

    # Summary stats
    profiles_updated: int = Field(0, description="Total profiles updated")
    photos_uploaded: int = Field(0, description="Total photos uploaded")
    signatures_pushed: int = Field(0, description="Total signatures pushed")


# =============================================================================
# Status Schemas
# =============================================================================


class EntraConnectionStatus(BaseModel):
    """Entra ID connection status."""

    connected: bool = Field(..., description="Whether connected to Entra ID")
    enabled: bool = Field(..., description="Whether Entra ID sync is enabled in config")
    tenant_id: str | None = Field(None, description="Azure AD tenant ID (masked)")
    client_id: str | None = Field(None, description="App registration client ID (masked)")
    error: str | None = Field(None, description="Connection error message")


class RoamingSignaturesStatus(BaseModel):
    """Status of roaming signatures in Exchange Online."""

    enabled: bool = Field(..., description="Whether roaming signatures are enabled")
    warning: str | None = Field(None, description="Warning message if roaming signatures may override server-side")
