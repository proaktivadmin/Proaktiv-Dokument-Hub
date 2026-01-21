"""
Pydantic schemas for Employee model.
"""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Type Aliases
# =============================================================================

EmployeeStatus = Literal["active", "onboarding", "offboarding", "inactive"]


# =============================================================================
# Base Schema
# =============================================================================


class EmployeeBase(BaseModel):
    """Base schema with common employee fields."""

    office_id: UUID = Field(..., description="ID of the office this employee belongs to")
    vitec_employee_id: str | None = Field(None, description="Vitec Hub employeeId")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field("", max_length=100, description="Last name (can be empty)")
    title: str | None = Field(None, max_length=100, description="Job title")
    email: str | None = Field(None, max_length=255, description="Email address")
    phone: str | None = Field(None, max_length=50, description="Phone number")
    homepage_profile_url: str | None = Field(None, description="Homepage profile URL")
    linkedin_url: str | None = Field(None, description="LinkedIn profile URL")
    facebook_url: str | None = Field(None, description="Facebook profile URL")
    instagram_url: str | None = Field(None, description="Instagram profile URL")
    twitter_url: str | None = Field(None, description="Twitter profile URL")
    sharepoint_folder_url: str | None = Field(None, description="SharePoint folder URL")
    profile_image_url: str | None = Field(None, description="Profile image URL")
    description: str | None = Field(None, description="Profile description")
    system_roles: list[str] | None = Field(default_factory=list, description="Vitec Next system roles")

    status: EmployeeStatus = Field("active", description="Employment status")
    is_featured_broker: bool = Field(False, description="Whether the employee is a featured broker")
    start_date: date | None = Field(None, description="Employment start date")
    end_date: date | None = Field(None, description="Employment end date")
    hide_from_homepage_date: date | None = Field(None, description="Date to hide from homepage")
    delete_data_date: date | None = Field(None, description="Date to delete employee data")


# =============================================================================
# Create/Update Schemas
# =============================================================================


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""

    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee (all fields optional)."""

    office_id: UUID | None = None
    vitec_employee_id: str | None = None
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    title: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    homepage_profile_url: str | None = None
    linkedin_url: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    twitter_url: str | None = None
    sharepoint_folder_url: str | None = None
    profile_image_url: str | None = None
    description: str | None = None
    system_roles: list[str] | None = None

    status: EmployeeStatus | None = None
    is_featured_broker: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    hide_from_homepage_date: date | None = None
    delete_data_date: date | None = None


class StartOffboarding(BaseModel):
    """Schema for starting the offboarding process."""

    end_date: date = Field(..., description="Final day of employment")
    hide_from_homepage_date: date | None = Field(None, description="Date to hide from homepage")
    delete_data_date: date | None = Field(None, description="Date to delete data")


# =============================================================================
# Response Schemas
# =============================================================================


class OfficeMinimal(BaseModel):
    """Minimal office info for employee responses."""

    id: UUID
    name: str
    short_code: str
    color: str

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeBase):
    """Schema for employee responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeWithOffice(EmployeeResponse):
    """Schema for employee with office details."""

    office: OfficeMinimal
    full_name: str = Field(description="Computed full name")
    initials: str = Field(description="Computed initials for avatar")
    days_until_end: int | None = Field(None, description="Days until end date")

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for paginated employee list."""

    items: list[EmployeeWithOffice]
    total: int

    class Config:
        from_attributes = True


class EmployeeSyncResult(BaseModel):
    """Schema for employee sync results."""

    total: int
    synced: int
    created: int
    updated: int
    skipped: int
    missing_office: int
