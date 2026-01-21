"""
Template and TemplateVersion SQLAlchemy Models
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType

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
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Required fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'docx', 'pdf', 'xlsx'
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    azure_blob_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional fields
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    azure_blob_container: Mapped[str] = mapped_column(String(100), default="templates")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # 'draft', 'published', 'archived'
    version: Mapped[int] = mapped_column(Integer, default=1)
    preview_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="nb-NO")

    # HTML content storage (for HTML templates)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Array and JSON fields (using cross-database compatible types)
    vitec_merge_fields: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONType, nullable=True, default=dict)

    # Vitec Metadata Fields (V2.7)
    channel: Mapped[str] = mapped_column(String(20), default="pdf_email")
    template_type: Mapped[str] = mapped_column(String(50), default="Objekt/Kontakt")
    receiver_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    receiver: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_receivers: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    phases: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    assignment_types: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    ownership_types: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    departments: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    email_subject: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Layout References
    header_template_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("layout_partials.id", ondelete="SET NULL"), nullable=True
    )
    footer_template_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("layout_partials.id", ondelete="SET NULL"), nullable=True
    )

    # Margins (in cm)
    margin_top: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=Decimal("1.5"))
    margin_bottom: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=Decimal("1.0"))
    margin_left: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=Decimal("1.0"))
    margin_right: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), default=Decimal("1.2"))

    # Thumbnail
    preview_thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tags: Mapped[list["Tag"]] = relationship(  # noqa: F821
        "Tag", secondary=template_tags, back_populates="templates", lazy="selectin"
    )

    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        "Category", secondary=template_categories, back_populates="templates", lazy="selectin"
    )

    versions: Mapped[list["TemplateVersion"]] = relationship(
        "TemplateVersion", back_populates="template", cascade="all, delete-orphan", lazy="selectin"
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
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    template_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)

    # Required fields
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    azure_blob_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional fields
    change_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    template: Mapped["Template"] = relationship("Template", back_populates="versions")

    # Unique constraint
    __table_args__ = (Index("uq_template_version", "template_id", "version_number", unique=True),)

    def __repr__(self) -> str:
        return f"<TemplateVersion(template_id={self.template_id}, version={self.version_number})>"
