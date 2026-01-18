"""
Pydantic schemas for Firecrawl scrape endpoints.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class FirecrawlScrapeRequest(BaseModel):
    """Request payload for a single-page scrape."""

    url: HttpUrl = Field(..., description="URL to scrape")
    formats: Optional[List[str]] = Field(
        default=None,
        description="Requested formats (e.g. markdown, html, rawHtml, links, summary)",
    )
    only_main_content: Optional[bool] = Field(
        default=None,
        description="If true, extract main content only",
    )
    wait_for_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Wait time before scraping (ms)",
    )
    timeout_ms: Optional[int] = Field(
        default=None,
        ge=1000,
        description="Timeout for page load (ms)",
    )
    include_tags: Optional[List[str]] = Field(
        default=None,
        description="CSS selectors to include",
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None,
        description="CSS selectors to exclude",
    )


class FirecrawlScrapeBase(BaseModel):
    """Base fields for scrape responses."""

    id: UUID
    url: str
    status: str
    requested_formats: List[str] = Field(default_factory=list)
    only_main_content: bool
    wait_for_ms: Optional[int] = None
    timeout_ms: Optional[int] = None
    include_tags: List[str] = Field(default_factory=list)
    exclude_tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FirecrawlScrapeDetail(FirecrawlScrapeBase):
    """Full scrape response with stored results."""

    result_markdown: Optional[str] = None
    result_html: Optional[str] = None
    result_raw_html: Optional[str] = None
    result_links: List[str] = Field(default_factory=list)
    result_metadata: Optional[Dict[str, Any]] = None
    result_json: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class FirecrawlScrapeListResponse(BaseModel):
    """Paginated response for scrapes."""

    items: List[FirecrawlScrapeBase]
    total: int

    class Config:
        from_attributes = True
