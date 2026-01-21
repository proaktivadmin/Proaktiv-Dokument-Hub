"""
Pydantic schemas for Firecrawl scrape endpoints.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class FirecrawlScrapeRequest(BaseModel):
    """Request payload for a single-page scrape."""

    url: HttpUrl = Field(..., description="URL to scrape")
    formats: list[str] | None = Field(
        default=None,
        description="Requested formats (e.g. markdown, html, rawHtml, links, summary)",
    )
    only_main_content: bool | None = Field(
        default=None,
        description="If true, extract main content only",
    )
    wait_for_ms: int | None = Field(
        default=None,
        ge=0,
        description="Wait time before scraping (ms)",
    )
    timeout_ms: int | None = Field(
        default=None,
        ge=1000,
        description="Timeout for page load (ms)",
    )
    include_tags: list[str] | None = Field(
        default=None,
        description="CSS selectors to include",
    )
    exclude_tags: list[str] | None = Field(
        default=None,
        description="CSS selectors to exclude",
    )


class FirecrawlScrapeBase(BaseModel):
    """Base fields for scrape responses."""

    id: UUID
    url: str
    status: str
    requested_formats: list[str] = Field(default_factory=list)
    only_main_content: bool
    wait_for_ms: int | None = None
    timeout_ms: int | None = None
    include_tags: list[str] = Field(default_factory=list)
    exclude_tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FirecrawlScrapeDetail(FirecrawlScrapeBase):
    """Full scrape response with stored results."""

    result_markdown: str | None = None
    result_html: str | None = None
    result_raw_html: str | None = None
    result_links: list[str] = Field(default_factory=list)
    result_metadata: dict[str, Any] | None = None
    result_json: dict[str, Any] | None = None
    error: str | None = None

    class Config:
        from_attributes = True


class FirecrawlScrapeListResponse(BaseModel):
    """Paginated response for scrapes."""

    items: list[FirecrawlScrapeBase]
    total: int

    class Config:
        from_attributes = True
