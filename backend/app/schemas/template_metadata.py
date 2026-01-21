"""
Pydantic schemas for extended Template Metadata (Vitec parity).
"""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateMetadataUpdate(BaseModel):
    """
    Schema for updating template Vitec metadata fields.
    All fields are optional for partial updates.
    """

    # Channel and Type
    channel: Literal["pdf", "email", "sms", "pdf_email"] | None = Field(None, description="Template channel type")
    template_type: Literal["Objekt/Kontakt", "System"] | None = Field(None, description="Template type")

    # Receiver
    receiver_type: Literal["Egne/kundetilpasset", "Systemstandard"] | None = Field(None, description="Receiver type")
    receiver: (
        Literal[
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
        | None
    ) = Field(None, description="Primary receiver")
    extra_receivers: list[str] | None = Field(None, description="Additional receivers")

    # Filtering/Categorization
    phases: list[Literal["Oppdrag", "Markedsføring", "Visning", "Budrunde", "Kontrakt", "Oppgjør"]] | None = Field(
        None, description="Applicable phases"
    )
    assignment_types: list[str] | None = Field(None, description="Assignment types")
    ownership_types: list[Literal["Bolig", "Aksje", "Tomt", "Næring", "Hytte"]] | None = Field(
        None, description="Ownership types"
    )
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

    # Thumbnail
    preview_thumbnail_url: str | None = Field(None, description="Preview thumbnail URL")


class TemplateAnalysisResult(BaseModel):
    """Schema for template analysis result."""

    template_id: UUID
    merge_fields_found: list[str]
    conditions_found: list[str]
    loops_found: list[str]
    unknown_fields: list[str]
    analysis_timestamp: str
