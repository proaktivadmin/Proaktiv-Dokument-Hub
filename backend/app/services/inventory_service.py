"""
Inventory Service

Provides statistics and management for Vitec template registry sync status.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template
from app.models.vitec_registry import VitecTemplateRegistry


class InventoryService:
    """
    Service for managing and querying Vitec template inventory.
    """

    @staticmethod
    async def get_sync_stats(db: AsyncSession) -> dict[str, Any]:
        """
        Get inventory sync statistics.

        Returns:
            Dict with counts by sync status and overall coverage.
        """
        # Count by sync status
        status_query = select(
            VitecTemplateRegistry.sync_status, func.count(VitecTemplateRegistry.id).label("count")
        ).group_by(VitecTemplateRegistry.sync_status)

        result = await db.execute(status_query)
        status_counts = {row.sync_status: row.count for row in result}

        # Get total Vitec templates
        total_vitec = await db.scalar(select(func.count(VitecTemplateRegistry.id))) or 0

        # Get total local templates
        total_local = await db.scalar(select(func.count(Template.id))) or 0

        # Calculate synced percentage
        synced_count = status_counts.get("synced", 0)
        sync_percentage = (synced_count / total_vitec * 100) if total_vitec > 0 else 0

        return {
            "total_vitec_templates": total_vitec,
            "total_local_templates": total_local,
            "synced": status_counts.get("synced", 0),
            "missing": status_counts.get("missing", 0),
            "modified": status_counts.get("modified", 0),
            "local_only": status_counts.get("local_only", 0),
            "sync_percentage": round(sync_percentage, 1),
        }

    @staticmethod
    async def get_missing_templates(db: AsyncSession, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get list of templates that exist in Vitec but not locally.

        Args:
            db: Database session
            limit: Maximum number of results

        Returns:
            List of missing template info
        """
        query = select(VitecTemplateRegistry).where(VitecTemplateRegistry.sync_status == "missing").limit(limit)

        result = await db.execute(query)
        templates = result.scalars().all()

        return [
            {
                "id": str(t.id),
                "vitec_name": t.vitec_name,
                "vitec_type": t.vitec_type,
                "vitec_phase": t.vitec_phase,
                "vitec_category": t.vitec_category,
                "vitec_channel": t.vitec_channel,
                "description": t.description,
            }
            for t in templates
        ]

    @staticmethod
    async def get_by_phase(db: AsyncSession) -> dict[str, dict[str, int]]:
        """
        Get inventory stats grouped by phase.

        Returns:
            Dict with phase names as keys and status counts as values
        """
        query = select(
            VitecTemplateRegistry.vitec_phase,
            VitecTemplateRegistry.sync_status,
            func.count(VitecTemplateRegistry.id).label("count"),
        ).group_by(VitecTemplateRegistry.vitec_phase, VitecTemplateRegistry.sync_status)

        result = await db.execute(query)

        phase_stats: dict[str, dict[str, int]] = {}
        for row in result:
            phase = row.vitec_phase or "Ukategorisert"
            if phase not in phase_stats:
                phase_stats[phase] = {"synced": 0, "missing": 0, "modified": 0, "local_only": 0}
            phase_stats[phase][row.sync_status] = row.count

        return phase_stats

    @staticmethod
    async def update_sync_status(
        db: AsyncSession, registry_id: str, local_template_id: str | None, status: str
    ) -> VitecTemplateRegistry | None:
        """
        Update the sync status of a registry entry.

        Args:
            db: Database session
            registry_id: VitecTemplateRegistry ID
            local_template_id: Optional local template ID
            status: New sync status

        Returns:
            Updated registry entry or None if not found
        """
        import uuid as uuid_lib
        from datetime import datetime

        query = select(VitecTemplateRegistry).where(VitecTemplateRegistry.id == uuid_lib.UUID(registry_id))
        result = await db.execute(query)
        entry = result.scalar_one_or_none()

        if not entry:
            return None

        entry.sync_status = status
        entry.local_template_id = uuid_lib.UUID(local_template_id) if local_template_id else None
        entry.last_checked = datetime.now()

        await db.flush()
        return entry
