"""
Firecrawl Service - business logic for web scraping.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.config import settings
from app.models.firecrawl_scrape import FirecrawlScrape

try:
    from firecrawl import AsyncFirecrawl
except Exception:  # pragma: no cover - dependency may not be installed yet
    AsyncFirecrawl = None

logger = logging.getLogger(__name__)


class FirecrawlService:
    """Service for running and storing Firecrawl scrapes."""

    @staticmethod
    def is_configured() -> bool:
        return bool(settings.FIRECRAWL_API_KEY)

    @staticmethod
    def _get_client() -> "AsyncFirecrawl":
        if AsyncFirecrawl is None:
            raise RuntimeError("firecrawl-py is not installed")
        if not settings.FIRECRAWL_API_KEY:
            raise RuntimeError("FIRECRAWL_API_KEY is not configured")
        return AsyncFirecrawl(api_key=settings.FIRECRAWL_API_KEY)

    @staticmethod
    def _normalize_result(result: Any) -> Dict[str, Any]:
        if isinstance(result, dict):
            return result
        if hasattr(result, "model_dump"):
            return result.model_dump()
        data: Dict[str, Any] = {}
        for key in ("markdown", "html", "rawHtml", "raw_html", "links", "metadata", "json", "data", "success"):
            if hasattr(result, key):
                data[key] = getattr(result, key)
        return data

    @staticmethod
    def _extract_payload(result_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = result_data.get("data")
        if isinstance(payload, dict):
            return payload
        return result_data

    @staticmethod
    def _safe_list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        return []

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        return {}

    @staticmethod
    async def run_scrape(
        *,
        url: str,
        formats: Optional[List[str]],
        only_main_content: Optional[bool],
        wait_for_ms: Optional[int],
        timeout_ms: Optional[int],
        include_tags: Optional[List[str]],
        exclude_tags: Optional[List[str]],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        client = FirecrawlService._get_client()
        resolved_formats = formats or ["markdown"]
        resolved_only_main = (
            settings.FIRECRAWL_ONLY_MAIN_CONTENT if only_main_content is None else only_main_content
        )
        resolved_timeout = settings.FIRECRAWL_TIMEOUT_MS if timeout_ms is None else timeout_ms

        options: Dict[str, Any] = {
            "formats": resolved_formats,
            "only_main_content": resolved_only_main,
            "timeout": resolved_timeout,
        }
        if wait_for_ms is not None:
            options["wait_for"] = wait_for_ms
        if include_tags:
            options["include_tags"] = include_tags
        if exclude_tags:
            options["exclude_tags"] = exclude_tags

        result = await client.scrape(url, **options)
        normalized = FirecrawlService._normalize_result(result)
        payload = FirecrawlService._extract_payload(normalized)
        return normalized, payload

    @staticmethod
    async def create_and_run(
        db: AsyncSession,
        *,
        url: str,
        formats: Optional[List[str]],
        only_main_content: Optional[bool],
        wait_for_ms: Optional[int],
        timeout_ms: Optional[int],
        include_tags: Optional[List[str]],
        exclude_tags: Optional[List[str]],
    ) -> FirecrawlScrape:
        requested_formats = formats or ["markdown"]
        scrape = FirecrawlScrape(
            url=url,
            status="pending",
            requested_formats=requested_formats,
            only_main_content=settings.FIRECRAWL_ONLY_MAIN_CONTENT
            if only_main_content is None
            else only_main_content,
            wait_for_ms=wait_for_ms,
            timeout_ms=timeout_ms if timeout_ms is not None else settings.FIRECRAWL_TIMEOUT_MS,
            include_tags=include_tags or [],
            exclude_tags=exclude_tags or [],
        )
        db.add(scrape)
        await db.flush()

        try:
            normalized, payload = await FirecrawlService.run_scrape(
                url=url,
                formats=formats,
                only_main_content=only_main_content,
                wait_for_ms=wait_for_ms,
                timeout_ms=timeout_ms,
                include_tags=include_tags,
                exclude_tags=exclude_tags,
            )

            scrape.status = "completed"
            scrape.result_markdown = payload.get("markdown")
            scrape.result_html = payload.get("html")
            scrape.result_raw_html = payload.get("rawHtml") or payload.get("raw_html")
            scrape.result_links = FirecrawlService._safe_list(payload.get("links"))
            scrape.result_metadata = FirecrawlService._safe_dict(payload.get("metadata"))
            scrape.result_json = FirecrawlService._safe_dict(normalized)
            scrape.error = None
        except Exception as exc:
            scrape.status = "failed"
            scrape.error = str(exc)
            logger.exception("Firecrawl scrape failed for %s", url)

        await db.flush()
        await db.refresh(scrape)
        return scrape

    @staticmethod
    async def list_scrapes(
        db: AsyncSession,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[FirecrawlScrape], int]:
        query = select(FirecrawlScrape)
        count_query = select(func.count()).select_from(FirecrawlScrape)

        if status:
            query = query.where(FirecrawlScrape.status == status)
            count_query = count_query.where(FirecrawlScrape.status == status)

        query = query.order_by(FirecrawlScrape.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        items = list(result.scalars().all())

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        return items, total

    @staticmethod
    async def get_by_id(db: AsyncSession, scrape_id: str) -> Optional[FirecrawlScrape]:
        result = await db.execute(
            select(FirecrawlScrape).where(FirecrawlScrape.id == str(scrape_id))
        )
        return result.scalar_one_or_none()
