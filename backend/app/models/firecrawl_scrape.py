"""
FirecrawlScrape SQLAlchemy Model

Stores scrape requests and results from Firecrawl for later review / reuse.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import GUID, Base, JSONType


class FirecrawlScrape(Base):
    """A single-page scrape request + stored result payload."""

    __tablename__ = "firecrawl_scrapes"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Request
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    requested_formats: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    only_main_content: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    wait_for_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timeout_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    include_tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    exclude_tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)

    # Result (selected fields)
    result_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_links: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True, default=list)
    result_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True, default=dict)
    result_json: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True, default=dict)

    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_firecrawl_scrapes_created_at", "created_at"),
        Index("idx_firecrawl_scrapes_status", "status"),
    )
