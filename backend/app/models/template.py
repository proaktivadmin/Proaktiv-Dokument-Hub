"""
Template and TemplateVersion SQLAlchemy Models
"""

from sqlalchemy import (
    Column, String, Text, BigInteger, Integer, DateTime, ForeignKey, Table, Index, Numeric
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
import uuid

from app.models.base import Base, GUID, JSONType


# Junction table: Template <-> Tag (many-to-many)
template_tags = Table(
    "template_tags",
    Base.metadata,
    Column("template_id", GUID, ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", GUID, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# Junction table: Template <-> Category (many-to-many)
template_categories = Table(
    "template_categories",
    Base.metadata,
    Column("template_id", GUID, ForeignKey("templates.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", GUID, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Template(Base):
    """
    Template model representing a document template.
    
    Stores metadata about templates uploaded to Azure Blob Storage.
    """
    
    __tablename__ = "templates"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Required fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'docx', 'pdf', 'xlsx'
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    azure_blob_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    azure_blob_container: Mapped[str] = mapped_column(String(100), default="templates")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # 'draft', 'published', 'archived'
    version: Mapped[int] = mapped_column(Integer, default=1)
    preview_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="nb-NO")
    
    # HTML content storage (for HTML templates)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Array and JSON fields (using cross-database compatible types)
    vitec_merge_fields: Mapped[Optional[List[str]]] = mapped_column(
        JSONType, 
        nullable=True,
        default=list
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONType, 
        nullable=True,
        default=dict
    )
    
    # Vitec Metadata Fields (V2.7)
    channel: Mapped[str] = mapped_column(String(20), default="pdf_email")
    template_type: Mapped[str] = mapped_column(String(50), default="Objekt/Kontakt")
    receiver_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    receiver: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extra_receivers: Mapped[Optional[List[str]]] = mapped_column(
        JSONType,
        nullable=True,
        default=list
    )
    phases: Mapped[Optional[List[str]]] = mapped_column(
        JSONType,
        nullable=True,
        default=list
    )
    assignment_types: Mapped[Optional[List[str]]] = mapped_column(
        JSONType,
        nullable=True,
        default=list
    )
    ownership_types: Mapped[Optional[List[str]]] = mapped_column(
        JSONType,
        nullable=True,
        default=list
    )
    departments: Mapped[Optional[List[str]]] = mapped_column(
        JSONType,
        nullable=True,
        default=list
    )
    email_subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Layout References
    header_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("layout_partials.id", ondelete="SET NULL"),
        nullable=True
    )
    footer_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("layout_partials.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Margins (in cm)
    margin_top: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        default=Decimal("1.5")
    )
    margin_bottom: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        default=Decimal("1.0")
    )
    margin_left: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        default=Decimal("1.0")
    )
    margin_right: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        default=Decimal("1.2")
    )
    
    # Thumbnail
    preview_thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relationships
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=template_tags,
        back_populates="templates",
        lazy="selectin"
    )
    
    categories: Mapped[List["Category"]] = relationship(
        "Category",
        secondary=template_categories,
        back_populates="templates",
        lazy="selectin"
    )
    
    versions: Mapped[List["TemplateVersion"]] = relationship(
        "TemplateVersion",
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_templates_status", "status"),
        Index("idx_templates_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Template(id={self.id}, title='{self.title}', status='{self.status}')>"


class TemplateVersion(Base):
    """
    Template version history.
    
    Stores previous versions of templates for version control.
    """
    
    __tablename__ = "template_versions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign key
    template_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Required fields
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    azure_blob_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Optional fields
    change_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="versions"
    )
    
    # Unique constraint
    __table_args__ = (
        Index("uq_template_version", "template_id", "version_number", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<TemplateVersion(template_id={self.template_id}, version={self.version_number})>"

