"""
Layout Partial Service - Business logic for headers and footers.
"""

import logging
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.layout_partial import LayoutPartial
from app.models.template import Template

logger = logging.getLogger(__name__)


class LayoutPartialService:
    """
    Service class for layout partial (header/footer) operations.
    """

    @staticmethod
    async def get_list(
        db: AsyncSession,
        *,
        type_filter: Literal["header", "footer"] | None = None,
        context_filter: Literal["pdf", "email", "all"] | None = None,
    ) -> list[LayoutPartial]:
        """
        Get list of layout partials with filters.

        Args:
            db: Database session
            type_filter: Filter by type (header/footer)
            context_filter: Filter by context (pdf/email/all)

        Returns:
            List of layout partials
        """
        query = select(LayoutPartial)

        if type_filter:
            query = query.where(LayoutPartial.type == type_filter)

        if context_filter:
            query = query.where(LayoutPartial.context == context_filter)

        query = query.order_by(LayoutPartial.type, LayoutPartial.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, partial_id: UUID) -> LayoutPartial | None:
        """
        Get a layout partial by ID.

        Args:
            db: Database session
            partial_id: Partial UUID

        Returns:
            LayoutPartial or None
        """
        result = await db.execute(select(LayoutPartial).where(LayoutPartial.id == partial_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_default(
        db: AsyncSession,
        *,
        type_filter: Literal["header", "footer"],
        context_filter: Literal["pdf", "email", "all"] = "all",
    ) -> LayoutPartial | None:
        """
        Get the default partial for a type/context combination.

        Args:
            db: Database session
            type_filter: Type (header/footer)
            context_filter: Context (pdf/email/all)

        Returns:
            Default LayoutPartial or None
        """
        result = await db.execute(
            select(LayoutPartial)
            .where(LayoutPartial.type == type_filter)
            .where(LayoutPartial.context == context_filter)
            .where(LayoutPartial.is_default)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        type: Literal["header", "footer"],
        html_content: str,
        created_by: str,
        context: Literal["pdf", "email", "all"] = "all",
        is_default: bool = False,
    ) -> LayoutPartial:
        """
        Create a new layout partial.

        Args:
            db: Database session
            name: Partial name
            type: Type (header/footer)
            html_content: HTML content
            created_by: User email
            context: Usage context
            is_default: Set as default

        Returns:
            Created partial
        """
        # If setting as default, unset any existing default
        if is_default:
            await db.execute(
                update(LayoutPartial)
                .where(LayoutPartial.type == type)
                .where(LayoutPartial.context == context)
                .where(LayoutPartial.is_default)
                .values(is_default=False)
            )

        partial = LayoutPartial(
            name=name,
            type=type,
            context=context,
            html_content=html_content,
            is_default=is_default,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(partial)
        await db.flush()
        await db.refresh(partial)
        return partial

    @staticmethod
    async def update(db: AsyncSession, partial: LayoutPartial, *, updated_by: str, **updates) -> LayoutPartial:
        """
        Update a layout partial.

        Args:
            db: Database session
            partial: Partial to update
            updated_by: User email
            **updates: Fields to update

        Returns:
            Updated partial
        """
        for key, value in updates.items():
            if hasattr(partial, key) and value is not None:
                setattr(partial, key, value)

        partial.updated_by = updated_by
        await db.flush()
        await db.refresh(partial)
        return partial

    @staticmethod
    async def delete(db: AsyncSession, partial: LayoutPartial) -> None:
        """
        Delete a layout partial.

        Args:
            db: Database session
            partial: Partial to delete

        Raises:
            HTTPException: If partial is in use by templates
        """
        # Check if partial is in use
        header_count_result = await db.execute(
            select(func.count(Template.id)).where(Template.header_template_id == partial.id)
        )
        footer_count_result = await db.execute(
            select(func.count(Template.id)).where(Template.footer_template_id == partial.id)
        )

        header_count = header_count_result.scalar() or 0
        footer_count = footer_count_result.scalar() or 0

        if header_count > 0 or footer_count > 0:
            raise HTTPException(
                status_code=409, detail=f"Partial is in use by {header_count + footer_count} template(s)"
            )

        await db.delete(partial)
        await db.flush()

    @staticmethod
    async def set_default(db: AsyncSession, partial: LayoutPartial) -> UUID | None:
        """
        Set a partial as the default for its type/context.
        Unsets any existing default.

        Args:
            db: Database session
            partial: Partial to set as default

        Returns:
            UUID of previous default (if any)
        """
        # Find current default
        result = await db.execute(
            select(LayoutPartial)
            .where(LayoutPartial.type == partial.type)
            .where(LayoutPartial.context == partial.context)
            .where(LayoutPartial.is_default)
            .where(LayoutPartial.id != partial.id)
        )
        previous_default = result.scalar_one_or_none()
        previous_default_id = previous_default.id if previous_default else None

        # Unset previous default
        if previous_default:
            previous_default.is_default = False

        # Set new default
        partial.is_default = True

        await db.flush()
        return previous_default_id
