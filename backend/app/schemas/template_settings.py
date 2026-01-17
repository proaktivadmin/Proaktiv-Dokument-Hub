"""
Pydantic schemas for Template Settings operations.

Based on Vitec Next configuration from .cursor/vitec-reference.md
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from uuid import UUID
from decimal import Decimal
from datetime import datetime


# =============================================================================
# VITEC TYPE DEFINITIONS (from vitec-reference.md)
# =============================================================================

# Template channel types
ChannelType = Literal['pdf', 'email', 'sms', 'pdf_email']

# Template types
TemplateType = Literal['Objekt/Kontakt', 'System']

# Receiver types
ReceiverType = Literal['Egne/kundetilpasset', 'Systemstandard']

# Primary receivers (from Kunderelasjonstyper - expanded)
PrimaryReceiver = Literal[
    'Selger', 'Kjoper', 'Megler', 'Bank', 'Forretningsforer',
    'Visningsdeltager', 'Budgiver', 'Interessent', 'Utleier', 'Leietaker',
    'Hjemmelshaver', 'Arving', 'Grunneier', 'Bortefester', 'Tinglysning',
    'Forening', 'Forsikringsselskap', 'Advokat', 'Takstmann', 'Fotograf',
    'Samarbeidspartner', 'Annen'
]

# Phases (from Vitec Faser - expanded)
VitecPhase = Literal[
    'Innsalg', 'Til salgs', 'Klargjoring', 'Kontrakt', 'Oppgjor',
    '2 faser', '3 faser', '4 faser'
]

# Ownership types (from Objektstyper Eieform)
OwnershipType = Literal[
    'Selveier', 'Andel', 'Aksje', 'Obligasjon', 'Tomt', 
    'Naering', 'Hytte', 'Borettslag', 'Sameie'
]


class TemplateContentUpdate(BaseModel):
    """Schema for updating template HTML content."""
    content: str = Field(..., min_length=1, description="HTML content")
    change_notes: Optional[str] = Field(None, max_length=500, description="Notes about the change")
    auto_sanitize: bool = Field(False, description="Sanitize HTML for Vitec compatibility")


class TemplateContentResponse(BaseModel):
    """Schema for template content update response."""
    id: UUID
    version: int
    content_hash: str
    merge_fields_detected: int
    previous_version_id: Optional[UUID] = None


class TemplateSettingsUpdate(BaseModel):
    """
    Schema for updating template Vitec settings.
    All fields are optional for partial updates.
    
    Based on Vitec Next configuration from vitec-reference.md.
    """
    # Channel and Type
    channel: Optional[ChannelType] = Field(
        None, description="Template channel type"
    )
    template_type: Optional[TemplateType] = Field(
        None, description="Template type"
    )
    
    # Receiver
    receiver_type: Optional[ReceiverType] = Field(
        None, description="Receiver type"
    )
    receiver: Optional[PrimaryReceiver] = Field(
        None, description="Primary receiver"
    )
    extra_receivers: Optional[List[str]] = Field(
        None, description="Additional receivers"
    )
    
    # Filtering/Categorization
    phases: Optional[List[VitecPhase]] = Field(
        None, description="Applicable phases (from Vitec Faser)"
    )
    assignment_types: Optional[List[str]] = Field(
        None, description="Assignment types"
    )
    ownership_types: Optional[List[OwnershipType]] = Field(
        None, description="Ownership types (from Vitec Eieform)"
    )
    departments: Optional[List[str]] = Field(
        None, description="Departments"
    )
    
    # Email
    email_subject: Optional[str] = Field(
        None, max_length=500, description="Email subject line (can include merge fields)"
    )
    
    # Layout
    header_template_id: Optional[UUID] = Field(
        None, description="Header layout partial ID"
    )
    footer_template_id: Optional[UUID] = Field(
        None, description="Footer layout partial ID"
    )
    
    # Margins (in cm)
    margin_top: Optional[Decimal] = Field(
        None, ge=0, le=10, description="Top margin in cm"
    )
    margin_bottom: Optional[Decimal] = Field(
        None, ge=0, le=10, description="Bottom margin in cm"
    )
    margin_left: Optional[Decimal] = Field(
        None, ge=0, le=10, description="Left margin in cm"
    )
    margin_right: Optional[Decimal] = Field(
        None, ge=0, le=10, description="Right margin in cm"
    )


class TemplateSettingsResponse(BaseModel):
    """Schema for template settings response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    channel: Optional[str] = None
    template_type: Optional[str] = None
    receiver_type: Optional[str] = None
    receiver: Optional[str] = None
    extra_receivers: List[str] = []
    phases: List[str] = []
    assignment_types: List[str] = []
    ownership_types: List[str] = []
    departments: List[str] = []
    email_subject: Optional[str] = None
    header_template_id: Optional[UUID] = None
    footer_template_id: Optional[UUID] = None
    margin_top: Optional[Decimal] = None
    margin_bottom: Optional[Decimal] = None
    margin_left: Optional[Decimal] = None
    margin_right: Optional[Decimal] = None
    updated_at: datetime


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics."""
    total: int
    published: int
    draft: int
    archived: int
    downloads: int
    recent_uploads: List[dict]
