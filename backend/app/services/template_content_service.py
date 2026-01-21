"""
Template Content Service - Handles saving and versioning template content.
"""

import hashlib
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template, TemplateVersion
from app.services.sanitizer_service import SanitizerService
from app.services.template_analyzer_service import TemplateAnalyzerService

logger = logging.getLogger(__name__)


class TemplateContentService:
    """
    Service for template content operations including versioning.
    """

    @staticmethod
    async def save_content(
        db: AsyncSession,
        template_id: UUID,
        *,
        content: str,
        updated_by: str,
        change_notes: str | None = None,
        auto_sanitize: bool = False,
    ) -> dict:
        """
        Save template HTML content with automatic versioning.

        Args:
            db: Database session
            template_id: Template UUID
            content: New HTML content
            updated_by: User email
            change_notes: Optional notes about the change
            auto_sanitize: Whether to sanitize the HTML (manual by default)

        Returns:
            Dict containing:
            - id: Template UUID
            - version: New version number
            - content_hash: SHA256 hash of content
            - merge_fields_detected: Count of merge fields
            - previous_version_id: UUID of version snapshot (if created)

        Raises:
            HTTPException: If template not found or not HTML
        """
        # Get template (convert UUID to string for SQLite compatibility)
        template_id_str = str(template_id)
        result = await db.execute(select(Template).where(Template.id == template_id_str))
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.file_type != "html":
            raise HTTPException(status_code=400, detail="Can only save content for HTML templates")

        # Compute hash of new content
        new_hash = TemplateContentService.compute_content_hash(content)

        # Check if content has actually changed
        old_hash = None
        if template.content:
            old_hash = TemplateContentService.compute_content_hash(template.content)

        previous_version_id = None

        # Create version snapshot if content changed
        if old_hash and old_hash != new_hash:
            version = await TemplateContentService.create_version_snapshot(
                db, template, created_by=updated_by, change_notes=change_notes
            )
            previous_version_id = version.id
            logger.info(f"Created version snapshot {version.id} for template {template_id}")

        # Sanitize content if requested
        processed_content = content
        if auto_sanitize:
            sanitizer = SanitizerService()
            processed_content = sanitizer.sanitize(content)
            logger.info(f"Sanitized content for template {template_id}")

        # Update template content
        template.content = processed_content
        template.updated_by = updated_by

        # Increment version number
        template.version += 1

        # Extract merge fields from new content
        merge_fields = TemplateAnalyzerService.extract_merge_fields(processed_content)
        template.vitec_merge_fields = merge_fields

        await db.flush()
        await db.refresh(template)

        logger.info(
            f"Saved content for template {template_id}, "
            f"version {template.version}, "
            f"found {len(merge_fields)} merge fields"
        )

        return {
            "id": template.id,
            "version": template.version,
            "content_hash": new_hash,
            "merge_fields_detected": len(merge_fields),
            "previous_version_id": previous_version_id,
        }

    @staticmethod
    async def create_version_snapshot(
        db: AsyncSession, template: Template, *, created_by: str, change_notes: str | None = None
    ) -> TemplateVersion:
        """
        Create a version snapshot of the current template state.

        Args:
            db: Database session
            template: Template to snapshot
            created_by: User email
            change_notes: Optional notes

        Returns:
            Created TemplateVersion
        """
        version = TemplateVersion(
            template_id=template.id,
            version_number=template.version,
            file_name=template.file_name,
            azure_blob_url=template.azure_blob_url,
            file_size_bytes=template.file_size_bytes,
            created_by=created_by,
            change_notes=change_notes,
        )

        db.add(version)
        await db.flush()
        await db.refresh(version)

        return version

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """
        Compute SHA256 hash of content.

        Args:
            content: String content

        Returns:
            Hex-encoded SHA256 hash
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
