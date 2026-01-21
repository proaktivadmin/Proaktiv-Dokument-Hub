"""
Merge Field Service - Business logic for Flettekode operations.
"""

import logging
import re
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merge_field import MergeField
from app.models.template import Template

logger = logging.getLogger(__name__)


class MergeFieldService:
    """
    Service class for merge field CRUD and discovery operations.

    Handles the Flettekode system including:
    - CRUD operations for merge fields
    - Auto-discovery of fields from templates
    - Search and filtering
    """

    # Regex patterns for Vitec merge field syntax
    MERGE_FIELD_PATTERN = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
    VITEC_IF_PATTERN = re.compile(r'vitec-if="([^"]+)"')
    VITEC_FOREACH_PATTERN = re.compile(r'vitec-foreach="(\w+)\s+in\s+([^"]+)"')

    @staticmethod
    async def get_list(
        db: AsyncSession,
        *,
        category: str | None = None,
        search: str | None = None,
        data_type: str | None = None,
        is_iterable: bool | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[MergeField], int]:
        """
        Get paginated list of merge fields with filters.

        Args:
            db: Database session
            category: Filter by category name
            search: Search in path, label, description
            data_type: Filter by data type
            is_iterable: Filter by iterable flag
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Tuple of (merge_fields list, total count)
        """
        # Build base query
        query = select(MergeField)
        count_query = select(func.count(MergeField.id))

        # Apply filters
        if category:
            query = query.where(MergeField.category == category)
            count_query = count_query.where(MergeField.category == category)

        if search:
            search_filter = or_(
                MergeField.path.ilike(f"%{search}%"),
                MergeField.label.ilike(f"%{search}%"),
                MergeField.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if data_type:
            query = query.where(MergeField.data_type == data_type)
            count_query = count_query.where(MergeField.data_type == data_type)

        if is_iterable is not None:
            query = query.where(MergeField.is_iterable == is_iterable)
            count_query = count_query.where(MergeField.is_iterable == is_iterable)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order_by(MergeField.category, MergeField.path)
        query = query.offset(offset).limit(per_page)

        # Execute query
        result = await db.execute(query)
        fields = list(result.scalars().all())

        return fields, total

    @staticmethod
    async def get_by_id(db: AsyncSession, field_id: UUID) -> MergeField | None:
        """
        Get a merge field by ID.

        Args:
            db: Database session
            field_id: Merge field UUID

        Returns:
            MergeField or None if not found
        """
        result = await db.execute(select(MergeField).where(MergeField.id == field_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_path(db: AsyncSession, path: str) -> MergeField | None:
        """
        Get a merge field by its path.

        Args:
            db: Database session
            path: Field path (e.g., 'selger.navn')

        Returns:
            MergeField or None if not found
        """
        result = await db.execute(select(MergeField).where(MergeField.path == path))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        path: str,
        category: str,
        label: str,
        description: str | None = None,
        example_value: str | None = None,
        data_type: str = "string",
        is_iterable: bool = False,
        parent_model: str | None = None,
    ) -> MergeField:
        """
        Create a new merge field.

        Args:
            db: Database session
            path: Unique field path
            category: Category name
            label: Display label
            description: Optional description
            example_value: Example value for preview
            data_type: Data type (string, number, date, boolean, array)
            is_iterable: Whether field can be used in foreach
            parent_model: Parent model path

        Returns:
            Created merge field
        """
        field = MergeField(
            path=path,
            category=category,
            label=label,
            description=description,
            example_value=example_value,
            data_type=data_type,
            is_iterable=is_iterable,
            parent_model=parent_model,
        )
        db.add(field)
        await db.flush()
        await db.refresh(field)
        return field

    @staticmethod
    async def update(db: AsyncSession, field: MergeField, **updates) -> MergeField:
        """
        Update a merge field.

        Args:
            db: Database session
            field: MergeField to update
            **updates: Fields to update

        Returns:
            Updated merge field
        """
        for key, value in updates.items():
            if hasattr(field, key) and value is not None:
                setattr(field, key, value)

        await db.flush()
        await db.refresh(field)
        return field

    @staticmethod
    async def delete(db: AsyncSession, field: MergeField) -> None:
        """
        Delete a merge field.

        Args:
            db: Database session
            field: MergeField to delete
        """
        await db.delete(field)
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
        result = await db.execute(select(MergeField.category).distinct().order_by(MergeField.category))
        return [row[0] for row in result.all()]

    @staticmethod
    async def search_autocomplete(db: AsyncSession, query: str, limit: int = 10) -> list[MergeField]:
        """
        Search merge fields for autocomplete suggestions.

        Args:
            db: Database session
            query: Search query
            limit: Maximum results

        Returns:
            List of matching merge fields
        """
        search_filter = or_(MergeField.path.ilike(f"%{query}%"), MergeField.label.ilike(f"%{query}%"))

        result = await db.execute(
            select(MergeField).where(search_filter).order_by(MergeField.usage_count.desc()).limit(limit)
        )
        return list(result.scalars().all())

    @classmethod
    async def discover_from_template(cls, db: AsyncSession, template: Template) -> dict:
        """
        Extract merge fields from a single template's content.

        Args:
            db: Database session
            template: Template to analyze

        Returns:
            Dict with discovered fields, conditions, loops
        """
        content = template.content or ""

        # Extract merge fields [[field.name]]
        merge_fields = set()
        for match in cls.MERGE_FIELD_PATTERN.finditer(content):
            field_path = match.group(2).strip()
            merge_fields.add(field_path)

        # Extract conditions vitec-if="..."
        conditions = set()
        for match in cls.VITEC_IF_PATTERN.finditer(content):
            conditions.add(match.group(1))

        # Extract loops vitec-foreach="item in collection"
        loops = []
        for match in cls.VITEC_FOREACH_PATTERN.finditer(content):
            loops.append({"variable": match.group(1), "collection": match.group(2)})

        return {"merge_fields": list(merge_fields), "conditions": list(conditions), "loops": loops}

    @classmethod
    async def discover_all(cls, db: AsyncSession, *, create_missing: bool = True) -> dict:
        """
        Scan all templates and discover merge fields.

        Args:
            db: Database session
            create_missing: If True, create new MergeField records for unknown fields

        Returns:
            Dict with discovery statistics
        """
        # Get all HTML templates
        result = await db.execute(
            select(Template).where(Template.file_type == "html").where(Template.content.isnot(None))
        )
        templates = list(result.scalars().all())

        # Get existing merge fields
        existing_result = await db.execute(select(MergeField.path))
        existing_paths = {row[0] for row in existing_result.all()}

        # Discover from all templates
        all_discovered = set()
        for template in templates:
            discovery = await cls.discover_from_template(db, template)
            all_discovered.update(discovery["merge_fields"])

        # Separate new and existing
        new_fields = list(all_discovered - existing_paths)
        existing_fields = list(all_discovered & existing_paths)

        # Optionally create new fields
        if create_missing:
            for path in new_fields:
                # Infer category from path
                category = "Ukjent"
                if "." in path:
                    prefix = path.split(".")[0].lower()
                    category_map = {
                        "selger": "Selger",
                        "kjoper": "Kjøper",
                        "eiendom": "Eiendom",
                        "megler": "Megler",
                        "ansvarligmegler": "Megler",
                        "meglerkontor": "Megler",
                        "oppdrag": "Økonomi",
                        "oppgjor": "Megler",
                    }
                    category = category_map.get(prefix, "Ukjent")

                await cls.create(
                    db,
                    path=path,
                    category=category,
                    label=path.replace(".", " ").title(),
                    data_type="string",
                    is_iterable=False,
                )

        return {
            "discovered_count": len(all_discovered),
            "new_fields": new_fields,
            "existing_fields": existing_fields,
            "templates_scanned": len(templates),
        }

    @staticmethod
    async def increment_usage(db: AsyncSession, field_id: UUID) -> None:
        """
        Increment usage count for a merge field.

        Args:
            db: Database session
            field_id: Merge field UUID
        """
        result = await db.execute(select(MergeField).where(MergeField.id == field_id))
        field = result.scalar_one_or_none()
        if field:
            field.usage_count += 1
            await db.flush()
