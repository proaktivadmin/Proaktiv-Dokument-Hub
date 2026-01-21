"""
Web Crawl Router - Firecrawl endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.firecrawl import (
    FirecrawlScrapeDetail,
    FirecrawlScrapeListResponse,
    FirecrawlScrapeRequest,
)
from app.services.firecrawl_service import FirecrawlService

router = APIRouter(prefix="/web-crawl", tags=["Web Crawl"])


@router.post("/scrape", response_model=FirecrawlScrapeDetail, status_code=201)
async def scrape_url(
    data: FirecrawlScrapeRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Scrape a single URL and store the result.
    """
    if not FirecrawlService.is_configured():
        raise HTTPException(status_code=503, detail="Firecrawl is not configured")

    scrape = await FirecrawlService.create_and_run(
        db,
        url=str(data.url),
        formats=data.formats,
        only_main_content=data.only_main_content,
        wait_for_ms=data.wait_for_ms,
        timeout_ms=data.timeout_ms,
        include_tags=data.include_tags,
        exclude_tags=data.exclude_tags,
    )
    return scrape


@router.get("/scrapes", response_model=FirecrawlScrapeListResponse)
async def list_scrapes(
    status: str | None = Query(None, description="Filter by status (pending, completed, failed)"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List stored scrapes with optional status filter.
    """
    items, total = await FirecrawlService.list_scrapes(
        db,
        status=status,
        skip=skip,
        limit=limit,
    )
    return FirecrawlScrapeListResponse(items=items, total=total)


@router.get("/scrapes/{scrape_id}", response_model=FirecrawlScrapeDetail)
async def get_scrape(
    scrape_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single scrape record by ID.
    """
    scrape = await FirecrawlService.get_by_id(db, str(scrape_id))
    if not scrape:
        raise HTTPException(status_code=404, detail="Scrape not found")
    return scrape
