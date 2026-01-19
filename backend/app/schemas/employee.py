"""
Pydantic schemas for Employee model.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date
from uuid import UUID


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
    vitec_employee_id: Optional[str] = Field(None, description="Vitec Hub employeeId")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    homepage_profile_url: Optional[str] = Field(None, description="Homepage profile URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    sharepoint_folder_url: Optional[str] = Field(None, description="SharePoint folder URL")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    description: Optional[str] = Field(None, description="Profile description")
    system_roles: Optional[List[str]] = Field(default_factory=list, description="Vitec Next system roles")

    status: EmployeeStatus = Field("active", description="Employment status")
    start_date: Optional[date] = Field(None, description="Employment start date")
    end_date: Optional[date] = Field(None, description="Employment end date")
    hide_from_homepage_date: Optional[date] = Field(None, description="Date to hide from homepage")
    delete_data_date: Optional[date] = Field(None, description="Date to delete employee data")


# =============================================================================
# Create/Update Schemas
# =============================================================================

class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee (all fields optional)."""
    office_id: Optional[UUID] = None
    vitec_employee_id: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    homepage_profile_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    sharepoint_folder_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    description: Optional[str] = None
    system_roles: Optional[List[str]] = None

    status: Optional[EmployeeStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    hide_from_homepage_date: Optional[date] = None
    delete_data_date: Optional[date] = None


class StartOffboarding(BaseModel):
    """Schema for starting the offboarding process."""
    end_date: date = Field(..., description="Final day of employment")
    hide_from_homepage_date: Optional[date] = Field(None, description="Date to hide from homepage")
    delete_data_date: Optional[date] = Field(None, description="Date to delete data")


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
    days_until_end: Optional[int] = Field(None, description="Days until end date")
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Schema for paginated employee list."""
    items: List[EmployeeWithOffice]
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
