"""
Code Pattern Service - Business logic for reusable code patterns.
"""

import logging
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.code_pattern import CodePattern

logger = logging.getLogger(__name__)


class CodePatternService:
    """
    Service class for code pattern CRUD operations.

    Handles reusable HTML/Vitec code snippets.
    """

    @staticmethod
    async def get_list(
        db: AsyncSession, *, category: str | None = None, search: str | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[CodePattern], int]:
        """
        Get paginated list of code patterns with filters.

        Args:
            db: Database session
            category: Filter by category
            search: Search in name, description
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (patterns list, total count)
        """
        # Build base query
        query = select(CodePattern)
        count_query = select(func.count(CodePattern.id))

        # Apply filters
        if category:
            query = query.where(CodePattern.category == category)
            count_query = count_query.where(CodePattern.category == category)

        if search:
            search_filter = or_(CodePattern.name.ilike(f"%{search}%"), CodePattern.description.ilike(f"%{search}%"))
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order_by(CodePattern.category, CodePattern.name)
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        patterns = list(result.scalars().all())

        return patterns, total

    @staticmethod
    async def get_by_id(db: AsyncSession, pattern_id: UUID) -> CodePattern | None:
        """
        Get a code pattern by ID.

        Args:
            db: Database session
            pattern_id: Pattern UUID

        Returns:
            CodePattern or None
        """
        result = await db.execute(select(CodePattern).where(CodePattern.id == pattern_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        category: str,
        html_code: str,
        created_by: str,
        description: str | None = None,
        variables_used: list[str] | None = None,
    ) -> CodePattern:
        """
        Create a new code pattern.

        Args:
            db: Database session
            name: Pattern name
            category: Category
            html_code: HTML/Vitec code
            created_by: User email
            description: Optional description
            variables_used: List of merge field paths

        Returns:
            Created pattern
        """
        pattern = CodePattern(
            name=name,
            category=category,
            html_code=html_code,
            description=description,
            variables_used=variables_used or [],
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(pattern)
        await db.flush()
        await db.refresh(pattern)
        return pattern

    @staticmethod
    async def update(db: AsyncSession, pattern: CodePattern, *, updated_by: str, **updates) -> CodePattern:
        """
        Update a code pattern.

        Args:
            db: Database session
            pattern: Pattern to update
            updated_by: User email
            **updates: Fields to update

        Returns:
            Updated pattern
        """
        for key, value in updates.items():
            if hasattr(pattern, key) and value is not None:
                setattr(pattern, key, value)

        pattern.updated_by = updated_by
        await db.flush()
        await db.refresh(pattern)
        return pattern

    @staticmethod
    async def delete(db: AsyncSession, pattern: CodePattern) -> None:
        """
        Delete a code pattern.

        Args:
            db: Database session
            pattern: Pattern to delete
        """
        await db.delete(pattern)
        await db.flush()

    @staticmethod
    async def get_categories(db: AsyncSession) -> list[str]:
        """
        Get list of all unique categories.

        Args:
            db: Database session

        Returns:
            List of category names
        """
        result = await db.execute(select(CodePattern.category).distinct().order_by(CodePattern.category))
        return [row[0] for row in result.all()]

    @staticmethod
    async def increment_usage(db: AsyncSession, pattern_id: UUID) -> None:
        """
        Increment usage count for a code pattern.

        Args:
            db: Database session
            pattern_id: Pattern UUID
        """
        result = await db.execute(select(CodePattern).where(CodePattern.id == pattern_id))
        pattern = result.scalar_one_or_none()
        if pattern:
            pattern.usage_count += 1
            await db.flush()
