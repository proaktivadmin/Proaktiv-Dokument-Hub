"""
Template Settings Service - Handles template metadata and settings.
"""

import logging
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.layout_partial import LayoutPartial
from app.models.template import Template

logger = logging.getLogger(__name__)


class TemplateSettingsService:
    """
    Service for template settings and metadata operations.
    """

    @staticmethod
    async def update_settings(
        db: AsyncSession,
        template_id: UUID,
        *,
        updated_by: str,
        channel: str | None = None,
        template_type: str | None = None,
        receiver_type: str | None = None,
        receiver: str | None = None,
        extra_receivers: list[str] | None = None,
        phases: list[str] | None = None,
        assignment_types: list[str] | None = None,
        ownership_types: list[str] | None = None,
        departments: list[str] | None = None,
        email_subject: str | None = None,
        header_template_id: UUID | None = None,
        footer_template_id: UUID | None = None,
        margin_top: Decimal | None = None,
        margin_bottom: Decimal | None = None,
        margin_left: Decimal | None = None,
        margin_right: Decimal | None = None,
    ) -> Template:
        """
        Update template settings and metadata.

        Args:
            db: Database session
            template_id: Template UUID
            updated_by: User email
            **settings: Settings to update

        Returns:
            Updated template

        Raises:
            HTTPException: If template not found or invalid settings
        """
        # Get template (convert UUID to string for SQLite compatibility)
        template_id_str = str(template_id)
        result = await db.execute(select(Template).where(Template.id == template_id_str))
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Validate layout partials if provided
        if header_template_id:
            await TemplateSettingsService.validate_layout_partial(db, header_template_id, "header")
            template.header_template_id = header_template_id

        if footer_template_id:
            await TemplateSettingsService.validate_layout_partial(db, footer_template_id, "footer")
            template.footer_template_id = footer_template_id

        # Update fields (only if provided)
        if channel is not None:
            template.channel = channel
        if template_type is not None:
            template.template_type = template_type
        if receiver_type is not None:
            template.receiver_type = receiver_type
        if receiver is not None:
            template.receiver = receiver
        if extra_receivers is not None:
            template.extra_receivers = extra_receivers
        if phases is not None:
            template.phases = phases
        if assignment_types is not None:
            template.assignment_types = assignment_types
        if ownership_types is not None:
            template.ownership_types = ownership_types
        if departments is not None:
            template.departments = departments
        if email_subject is not None:
            template.email_subject = email_subject
        if margin_top is not None:
            template.margin_top = margin_top
        if margin_bottom is not None:
            template.margin_bottom = margin_bottom
        if margin_left is not None:
            template.margin_left = margin_left
        if margin_right is not None:
            template.margin_right = margin_right

        # Update metadata
        template.updated_by = updated_by

        await db.flush()
        await db.refresh(template)

        logger.info(f"Updated settings for template {template_id}")

        return template

    @staticmethod
    async def get_settings(db: AsyncSession, template_id: UUID) -> dict:
        """
        Get template settings as a dictionary.

        Args:
            db: Database session
            template_id: Template UUID

        Returns:
            Dict of settings

        Raises:
            HTTPException: If template not found
        """
        # Convert UUID to string for SQLite compatibility
        template_id_str = str(template_id)
        result = await db.execute(select(Template).where(Template.id == template_id_str))
        template = result.scalar_one_or_none()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Convert string IDs to UUID for Pydantic validation
        header_id = None
        if template.header_template_id:
            header_id = (
                UUID(template.header_template_id)
                if isinstance(template.header_template_id, str)
                else template.header_template_id
            )

        footer_id = None
        if template.footer_template_id:
            footer_id = (
                UUID(template.footer_template_id)
                if isinstance(template.footer_template_id, str)
                else template.footer_template_id
            )

        return {
            "id": UUID(template.id) if isinstance(template.id, str) else template.id,
            "title": template.title or "Untitled",
            "channel": template.channel,
            "template_type": template.template_type,
            "receiver_type": template.receiver_type,
            "receiver": template.receiver,
            "extra_receivers": template.extra_receivers or [],
            "phases": template.phases or [],
            "assignment_types": template.assignment_types or [],
            "ownership_types": template.ownership_types or [],
            "departments": template.departments or [],
            "email_subject": template.email_subject,
            "header_template_id": header_id,
            "footer_template_id": footer_id,
            "margin_top": template.margin_top,
            "margin_bottom": template.margin_bottom,
            "margin_left": template.margin_left,
            "margin_right": template.margin_right,
            "updated_at": template.updated_at,
        }

    @staticmethod
    async def validate_layout_partial(db: AsyncSession, partial_id: UUID, expected_type: str) -> bool:
        """
        Validate that a layout partial exists and is of the expected type.

        Args:
            db: Database session
            partial_id: LayoutPartial UUID
            expected_type: 'header' or 'footer'

        Returns:
            True if valid

        Raises:
            HTTPException: If partial not found or wrong type
        """
        result = await db.execute(select(LayoutPartial).where(LayoutPartial.id == partial_id))
        partial = result.scalar_one_or_none()

        if not partial:
            raise HTTPException(status_code=400, detail=f"Layout partial {partial_id} not found")

        if partial.type != expected_type:
            raise HTTPException(
                status_code=400,
                detail=f"Layout partial {partial_id} is type '{partial.type}', expected '{expected_type}'",
            )

        return True
