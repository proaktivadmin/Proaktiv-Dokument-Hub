"""
Pydantic schemas for Template Settings operations.

Based on Vitec Next configuration from .cursor/vitec-reference.md
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# VITEC TYPE DEFINITIONS (from vitec-reference.md)
# =============================================================================

# Template channel types
ChannelType = Literal["pdf", "email", "sms", "pdf_email"]

# Template types
TemplateType = Literal["Objekt/Kontakt", "System"]

# Receiver types
ReceiverType = Literal["Egne/kundetilpasset", "Systemstandard"]

# Primary receivers (from Kunderelasjonstyper - expanded)
PrimaryReceiver = Literal[
    "Selger",
    "Kjøper",
    "Megler",
    "Bank",
    "Forretningsfører",
    "Visningsdeltager",
    "Budgiver",
    "Interessent",
    "Interessent - Match",
    "Utleier",
    "Leietaker",
    "Borettslag",
    "Bank - selger",
    "Bank - kjøper",
    "Ikke interessert",
    "Hjemmelshaver",
    "Panthaver",
    "Saksøkt",
    "Kreditor",
    "Prosessfullmektig",
    "Saksøker",
    "Opprinnelig kjøper",
    "Fremleier",
    "Fremleietaker",
    "Takstmann",
    "Sameie",
    "Aksjeselskap",
    "Kommune",
    "Interessent - budoppfølging",
    "Interessent - autoprospekt",
    "Fester",
    "Fakturamottaker",
    "Hjemmelsutsteder",
    "Fullmektig",
    "Grunneier",
    "Tidligere eier/avdød",
    "Arving",
    "Selgers ektefelle",
    "Kontodisponent selger",
    "Kontodisponent kjøper",
    "Kartverket",
    "Advokat",
    "Fotograf",
    "Samarbeidspartner",
    "Annen",
    "Bortefester",
    "Tinglysning",
    "Forening",
    "Forsikringsselskap",
    "Kjoper",
    "Forretningsforer",
]

# Phases (from Vitec Faser - expanded)
VitecPhase = Literal["Innsalg", "Til salgs", "Klargjoring", "Kontrakt", "Oppgjor", "2 faser", "3 faser", "4 faser"]

# Ownership types (from Objektstyper Eieform)
OwnershipType = Literal["Selveier", "Andel", "Aksje", "Obligasjon", "Tomt", "Naering", "Hytte", "Borettslag", "Sameie"]


class TemplateContentUpdate(BaseModel):
    """Schema for updating template HTML content."""

    content: str = Field(..., min_length=1, description="HTML content")
    change_notes: str | None = Field(None, max_length=500, description="Notes about the change")
    auto_sanitize: bool = Field(False, description="Sanitize HTML for Vitec compatibility")


class TemplateContentResponse(BaseModel):
    """Schema for template content update response."""

    id: UUID
    version: int
    content_hash: str
    merge_fields_detected: int
    previous_version_id: UUID | None = None


class TemplateSettingsUpdate(BaseModel):
    """
    Schema for updating template Vitec settings.
    All fields are optional for partial updates.

    Based on Vitec Next configuration from vitec-reference.md.
    """

    # Channel and Type
    channel: ChannelType | None = Field(None, description="Template channel type")
    template_type: TemplateType | None = Field(None, description="Template type")

    # Receiver
    receiver_type: ReceiverType | None = Field(None, description="Receiver type")
    receiver: PrimaryReceiver | None = Field(None, description="Primary receiver")
    extra_receivers: list[str] | None = Field(None, description="Additional receivers")

    # Filtering/Categorization
    phases: list[VitecPhase] | None = Field(None, description="Applicable phases (from Vitec Faser)")
    assignment_types: list[str] | None = Field(None, description="Assignment types")
    ownership_types: list[OwnershipType] | None = Field(None, description="Ownership types (from Vitec Eieform)")
    departments: list[str] | None = Field(None, description="Departments")

    # Email
    email_subject: str | None = Field(None, max_length=500, description="Email subject line (can include merge fields)")

    # Layout
    header_template_id: UUID | None = Field(None, description="Header layout partial ID")
    footer_template_id: UUID | None = Field(None, description="Footer layout partial ID")

    # Margins (in cm)
    margin_top: Decimal | None = Field(None, ge=0, le=10, description="Top margin in cm")
    margin_bottom: Decimal | None = Field(None, ge=0, le=10, description="Bottom margin in cm")
    margin_left: Decimal | None = Field(None, ge=0, le=10, description="Left margin in cm")
    margin_right: Decimal | None = Field(None, ge=0, le=10, description="Right margin in cm")


class TemplateSettingsResponse(BaseModel):
    """Schema for template settings response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    channel: str | None = None
    template_type: str | None = None
    receiver_type: str | None = None
    receiver: str | None = None
    extra_receivers: list[str] = []
    phases: list[str] = []
    assignment_types: list[str] = []
    ownership_types: list[str] = []
    departments: list[str] = []
    email_subject: str | None = None
    header_template_id: UUID | None = None
    footer_template_id: UUID | None = None
    margin_top: Decimal | None = None
    margin_bottom: Decimal | None = None
    margin_left: Decimal | None = None
    margin_right: Decimal | None = None
    updated_at: datetime


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics."""

    total: int
    published: int
    draft: int
    archived: int
    downloads: int
    recent_uploads: list[dict]
