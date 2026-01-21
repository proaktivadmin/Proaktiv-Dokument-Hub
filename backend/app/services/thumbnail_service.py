"""
Thumbnail Service - Generate static thumbnails for templates.
"""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template
from app.services.azure_storage_service import get_azure_storage_service

logger = logging.getLogger(__name__)


class ThumbnailService:
    """
    Service for generating and storing template thumbnails.

    Uses Playwright to render HTML templates as images.
    Falls back gracefully if Playwright is not available.
    """

    THUMBNAIL_WIDTH = 210  # A4 width at ~72 DPI
    THUMBNAIL_HEIGHT = 297  # A4 height at ~72 DPI
    THUMBNAIL_SCALE = 0.5  # Scale factor for smaller file size

    @classmethod
    async def generate_thumbnail(cls, db: AsyncSession, template_id: UUID) -> dict:
        """
        Generate a thumbnail for a template.

        Args:
            db: Database session
            template_id: Template UUID

        Returns:
            Dict containing:
            - thumbnail_url: URL to the generated thumbnail
            - width: Thumbnail width in pixels
            - height: Thumbnail height in pixels

        Raises:
            HTTPException: If template not found or generation fails
        """
        from sqlalchemy import select

        # Get template (convert UUID to string for SQLite compatibility)
        template_id_str = str(template_id)
        result = await db.execute(select(Template).where(Template.id == template_id_str))
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.file_type != "html":
            raise HTTPException(status_code=400, detail="Can only generate thumbnails for HTML templates")

        if not template.content:
            raise HTTPException(status_code=400, detail="Template has no content")

        # Render HTML to image
        try:
            image_bytes = await cls.render_html_to_image(
                template.content, width=cls.THUMBNAIL_WIDTH, height=cls.THUMBNAIL_HEIGHT, scale=cls.THUMBNAIL_SCALE
            )
        except ImportError:
            raise HTTPException(
                status_code=501, detail="Thumbnail generation not available. Playwright is not installed."
            )
        except Exception as e:
            logger.error(f"Failed to render thumbnail: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate thumbnail: {str(e)}")

        # Upload to Azure Blob Storage
        storage = get_azure_storage_service()
        thumbnail_filename = f"thumbnails/{template_id}.png"

        try:
            thumbnail_url = await storage.upload_file(
                file_content=image_bytes, file_name=thumbnail_filename, content_type="image/png"
            )
        except Exception as e:
            logger.error(f"Failed to upload thumbnail: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload thumbnail: {str(e)}")

        # Update template with thumbnail URL
        template.preview_thumbnail_url = thumbnail_url
        await db.flush()
        await db.refresh(template)

        logger.info(f"Generated thumbnail for template {template_id}")

        return {
            "thumbnail_url": thumbnail_url,
            "width": int(cls.THUMBNAIL_WIDTH * cls.THUMBNAIL_SCALE),
            "height": int(cls.THUMBNAIL_HEIGHT * cls.THUMBNAIL_SCALE),
        }

    @classmethod
    async def render_html_to_image(
        cls, html_content: str, *, width: int = 210, height: int = 297, scale: float = 0.5
    ) -> bytes:
        """
        Render HTML content to a PNG image.

        Args:
            html_content: HTML to render
            width: Viewport width
            height: Viewport height
            scale: Scale factor

        Returns:
            PNG image bytes

        Raises:
            ImportError: If Playwright is not installed
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Playwright is not installed. Run: pip install playwright && playwright install chromium")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)

            await page.set_content(html_content)

            # Wait for any images or fonts to load
            await page.wait_for_load_state("networkidle")

            # Take screenshot
            screenshot_bytes = await page.screenshot(type="png", full_page=False)

            await browser.close()

            return screenshot_bytes

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if thumbnail generation is available.

        Returns:
            True if Playwright is installed and configured
        """
        try:
            import importlib.util

            return importlib.util.find_spec("playwright") is not None
        except ImportError:
            return False
