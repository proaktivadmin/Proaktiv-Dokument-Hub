"""
Pydantic schemas for signature override CRUD.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SignatureOverrideUpdate(BaseModel):
    """Request body for creating/updating signature overrides."""

    display_name: str | None = Field(None, max_length=200)
    job_title: str | None = Field(None, max_length=100)
    mobile_phone: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    office_name: str | None = Field(None, max_length=200)
    facebook_url: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    employee_url: str | None = None


class SignatureOverrideResponse(BaseModel):
    """Response model for signature overrides."""

    employee_id: UUID
    display_name: str | None = None
    job_title: str | None = None
    mobile_phone: str | None = None
    email: str | None = None
    office_name: str | None = None
    facebook_url: str | None = None
    instagram_url: str | None = None
    linkedin_url: str | None = None
    employee_url: str | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}
