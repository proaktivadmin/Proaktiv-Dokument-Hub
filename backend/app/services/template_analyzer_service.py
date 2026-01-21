"""
Template Analyzer Service - Analyzes templates for merge fields and patterns.
"""

import logging
import re
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.merge_field import MergeField
from app.models.template import Template

logger = logging.getLogger(__name__)


class TemplateAnalyzerService:
    """
    Service for analyzing template content.

    Extracts merge fields, conditions, and loops from template HTML.
    """

    # Regex patterns
    MERGE_FIELD_PATTERN = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
    VITEC_IF_PATTERN = re.compile(r'vitec-if="([^"]+)"')
    VITEC_FOREACH_PATTERN = re.compile(r'vitec-foreach="(\w+)\s+in\s+([^"]+)"')

    @classmethod
    async def analyze(cls, db: AsyncSession, template_id: UUID) -> dict:
        """
        Analyze a single template and return all discovered elements.

        Args:
            db: Database session
            template_id: Template UUID to analyze

        Returns:
            Dict containing:
            - template_id: UUID
            - merge_fields_found: List[str] - paths of merge fields
            - conditions_found: List[str] - condition expressions
            - loops_found: List[str] - loop expressions
            - unknown_fields: List[str] - fields not in merge_fields table
            - analysis_timestamp: ISO timestamp

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
            raise HTTPException(status_code=400, detail="Template is not HTML")

        if not template.content:
            raise HTTPException(status_code=400, detail="Template has no content")

        content = template.content

        # Extract merge fields
        merge_fields = cls.extract_merge_fields(content)

        # Extract conditions
        conditions = cls.extract_conditions(content)

        # Extract loops
        loops = cls.extract_loops(content)
        loop_expressions = [f"{loop['variable']} in {loop['collection']}" for loop in loops]

        # Get existing merge field paths
        existing_result = await db.execute(select(MergeField.path))
        existing_paths = {row[0] for row in existing_result.all()}

        # Find unknown fields
        unknown_fields = [f for f in merge_fields if f not in existing_paths]

        return {
            "template_id": template_id,
            "merge_fields_found": merge_fields,
            "conditions_found": conditions,
            "loops_found": loop_expressions,
            "unknown_fields": unknown_fields,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    @classmethod
    async def scan_all(cls, db: AsyncSession, *, update_usage_counts: bool = True) -> dict:
        """
        Scan all HTML templates in the database.

        Args:
            db: Database session
            update_usage_counts: If True, update merge field usage counts

        Returns:
            Dict containing:
            - templates_scanned: int
            - total_merge_fields: int
            - total_conditions: int
            - total_loops: int
            - unique_fields: List[str]
            - unknown_fields: List[str]
        """
        # Get all HTML templates
        result = await db.execute(
            select(Template).where(Template.file_type == "html").where(Template.content.isnot(None))
        )
        templates = list(result.scalars().all())

        # Aggregate results
        all_fields: set[str] = set()
        all_conditions: set[str] = set()
        all_loops: list[dict] = []
        field_usage: dict[str, int] = {}

        for template in templates:
            content = template.content or ""

            fields = cls.extract_merge_fields(content)
            conditions = cls.extract_conditions(content)
            loops = cls.extract_loops(content)

            all_fields.update(fields)
            all_conditions.update(conditions)
            all_loops.extend(loops)

            for field in fields:
                field_usage[field] = field_usage.get(field, 0) + 1

        # Get existing merge field paths
        existing_result = await db.execute(select(MergeField.path))
        existing_paths = {row[0] for row in existing_result.all()}

        # Find unknown fields
        unknown_fields = list(all_fields - existing_paths)

        # Update usage counts
        if update_usage_counts:
            for path, count in field_usage.items():
                field_result = await db.execute(select(MergeField).where(MergeField.path == path))
                field = field_result.scalar_one_or_none()
                if field:
                    field.usage_count = count
            await db.flush()

        return {
            "templates_scanned": len(templates),
            "total_merge_fields": len(all_fields),
            "total_conditions": len(all_conditions),
            "total_loops": len(all_loops),
            "unique_fields": list(all_fields),
            "unknown_fields": unknown_fields,
        }

    @classmethod
    def extract_merge_fields(cls, content: str) -> list[str]:
        """
        Extract merge field paths from content.

        Args:
            content: HTML content

        Returns:
            List of merge field paths
        """
        fields = set()
        for match in cls.MERGE_FIELD_PATTERN.finditer(content):
            field_path = match.group(2).strip()
            fields.add(field_path)
        return sorted(fields)

    @classmethod
    def extract_conditions(cls, content: str) -> list[str]:
        """
        Extract vitec-if conditions from content.

        Args:
            content: HTML content

        Returns:
            List of condition expressions
        """
        conditions = set()
        for match in cls.VITEC_IF_PATTERN.finditer(content):
            conditions.add(match.group(1))
        return sorted(conditions)

    @classmethod
    def extract_loops(cls, content: str) -> list[dict]:
        """
        Extract vitec-foreach loops from content.

        Args:
            content: HTML content

        Returns:
            List of dicts with 'variable' and 'collection' keys
        """
        loops = []
        for match in cls.VITEC_FOREACH_PATTERN.finditer(content):
            loops.append({"variable": match.group(1), "collection": match.group(2)})
        return loops
