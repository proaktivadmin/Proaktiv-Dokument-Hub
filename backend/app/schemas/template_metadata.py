"""
Pydantic schemas for extended Template Metadata (Vitec parity).
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID
from decimal import Decimal


class TemplateMetadataUpdate(BaseModel):
    """
    Schema for updating template Vitec metadata fields.
    All fields are optional for partial updates.
    """
    # Channel and Type
    channel: Optional[Literal['pdf', 'email', 'sms', 'pdf_email']] = Field(
        None, description="Template channel type"
    )
    template_type: Optional[Literal['Objekt/Kontakt', 'System']] = Field(
        None, description="Template type"
    )
    
    # Receiver
    receiver_type: Optional[Literal['Egne/kundetilpasset', 'Systemstandard']] = Field(
        None, description="Receiver type"
    )
    receiver: Optional[Literal[
        'Selger', 'Kjøper', 'Megler', 'Bank', 'Forretningsfører',
        'Visningsdeltager', 'Budgiver', 'Interessent', 'Interessent - Match',
        'Utleier', 'Leietaker', 'Borettslag', 'Bank - selger', 'Bank - kjøper',
        'Ikke interessert', 'Hjemmelshaver', 'Panthaver', 'Saksøkt', 'Kreditor',
        'Prosessfullmektig', 'Saksøker', 'Opprinnelig kjøper', 'Fremleier',
        'Fremleietaker', 'Takstmann', 'Sameie', 'Aksjeselskap', 'Kommune',
        'Interessent - budoppfølging', 'Interessent - autoprospekt',
        'Fester', 'Fakturamottaker', 'Hjemmelsutsteder', 'Fullmektig',
        'Grunneier', 'Tidligere eier/avdød', 'Arving', 'Selgers ektefelle',
        'Kontodisponent selger', 'Kontodisponent kjøper', 'Kartverket',
        'Advokat', 'Fotograf', 'Samarbeidspartner', 'Annen', 'Bortefester',
        'Tinglysning', 'Forening', 'Forsikringsselskap', 'Kjoper', 'Forretningsforer'
    ]] = Field(None, description="Primary receiver")
    extra_receivers: Optional[List[str]] = Field(
        None, description="Additional receivers"
    )
    
    # Filtering/Categorization
    phases: Optional[List[Literal['Oppdrag', 'Markedsføring', 'Visning', 'Budrunde', 'Kontrakt', 'Oppgjør']]] = Field(
        None, description="Applicable phases"
    )
    assignment_types: Optional[List[str]] = Field(
        None, description="Assignment types"
    )
    ownership_types: Optional[List[Literal['Bolig', 'Aksje', 'Tomt', 'Næring', 'Hytte']]] = Field(
        None, description="Ownership types"
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
    
    # Thumbnail
    preview_thumbnail_url: Optional[str] = Field(
        None, description="Preview thumbnail URL"
    )


class TemplateAnalysisResult(BaseModel):
    """Schema for template analysis result."""
    template_id: UUID
    merge_fields_found: List[str]
    conditions_found: List[str]
    loops_found: List[str]
    unknown_fields: List[str]
    analysis_timestamp: str
