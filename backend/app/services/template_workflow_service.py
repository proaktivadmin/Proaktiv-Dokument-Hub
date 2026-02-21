"""
Template Workflow Service — manages the publishing lifecycle.

State machine:
  draft → in_review  (requires non-empty content)
  in_review → published  (sets published_version)
  in_review → draft  (rejection)
  published → draft  (unpublish)
  any → archived
  archived → draft  (restore)
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template, TemplateVersion

logger = logging.getLogger(__name__)

VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"in_review", "archived"},
    "in_review": {"published", "draft", "archived"},
    "published": {"draft", "archived"},
    "archived": {"draft"},
}


class TemplateWorkflowService:
    """Manages template publishing workflow transitions."""

    @staticmethod
    async def _get_template(db: AsyncSession, template_id: UUID) -> Template:
        result = await db.execute(select(Template).where(Template.id == str(template_id)))
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template

    @staticmethod
    def _validate_transition(current: str, target: str) -> None:
        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{current}' to '{target}'. "
                f"Allowed transitions: {', '.join(sorted(allowed)) or 'none'}",
            )

    async def submit_for_review(self, db: AsyncSession, template_id: UUID) -> Template:
        """Move draft → in_review. Validates content is non-empty."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "in_review")

        if not template.content or not template.content.strip():
            raise HTTPException(status_code=400, detail="Cannot submit an empty template for review")

        old_status = template.workflow_status
        template.workflow_status = "in_review"

        await self._record_event(db, template, old_status, "in_review")
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s submitted for review", template_id)
        return template

    async def approve_and_publish(
        self, db: AsyncSession, template_id: UUID, reviewer: str
    ) -> Template:
        """Move in_review → published. Sets published_version, reviewed_at, reviewed_by."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "published")

        old_status = template.workflow_status
        now = datetime.now(UTC)
        template.workflow_status = "published"
        template.published_version = template.version
        template.reviewed_at = now
        template.reviewed_by = reviewer
        template.published_at = now

        await self._record_event(db, template, old_status, "published", actor=reviewer)
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s approved and published by %s", template_id, reviewer)
        return template

    async def reject_review(
        self, db: AsyncSession, template_id: UUID, reviewer: str, reason: str | None = None
    ) -> Template:
        """Move in_review → draft. Adds rejection reason to version notes."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "draft")

        old_status = template.workflow_status
        template.workflow_status = "draft"

        notes = f"Avvist: {reason}" if reason else "Avvist"
        await self._record_event(db, template, old_status, "draft", actor=reviewer, notes=notes)
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s rejected by %s: %s", template_id, reviewer, reason or "(no reason)")
        return template

    async def unpublish(self, db: AsyncSession, template_id: UUID) -> Template:
        """Move published → draft. Clears published_version."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "draft")

        old_status = template.workflow_status
        template.workflow_status = "draft"
        template.published_version = None

        await self._record_event(db, template, old_status, "draft", notes="Avpublisert")
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s unpublished", template_id)
        return template

    async def archive(self, db: AsyncSession, template_id: UUID) -> Template:
        """Move any state → archived."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "archived")

        old_status = template.workflow_status
        template.workflow_status = "archived"

        await self._record_event(db, template, old_status, "archived")
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s archived", template_id)
        return template

    async def restore(self, db: AsyncSession, template_id: UUID) -> Template:
        """Move archived → draft."""
        template = await self._get_template(db, template_id)
        self._validate_transition(template.workflow_status, "draft")

        old_status = template.workflow_status
        template.workflow_status = "draft"

        await self._record_event(db, template, old_status, "draft", notes="Gjenopprettet fra arkiv")
        await db.flush()
        await db.refresh(template)
        logger.info("Template %s restored from archive", template_id)
        return template

    async def get_workflow_history(self, db: AsyncSession, template_id: UUID) -> list[dict]:
        """Return version history entries related to workflow transitions."""
        await self._get_template(db, template_id)

        result = await db.execute(
            select(TemplateVersion)
            .where(TemplateVersion.template_id == str(template_id))
            .order_by(TemplateVersion.created_at.desc())
        )
        versions = result.scalars().all()

        events: list[dict] = []
        for v in versions:
            notes = v.change_notes or ""
            if notes.startswith("workflow:"):
                parts = notes.split("|", 3)
                events.append({
                    "timestamp": v.created_at.isoformat() if v.created_at else None,
                    "from_status": parts[1] if len(parts) > 1 else "",
                    "to_status": parts[2] if len(parts) > 2 else "",
                    "actor": v.created_by,
                    "notes": parts[3] if len(parts) > 3 else None,
                })
        return events

    @staticmethod
    async def _record_event(
        db: AsyncSession,
        template: Template,
        from_status: str,
        to_status: str,
        *,
        actor: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Record a workflow transition as a TemplateVersion entry."""
        change_notes = f"workflow:{from_status}|{to_status}"
        if notes:
            change_notes += f"|{notes}"

        version = TemplateVersion(
            template_id=template.id,
            version_number=template.version,
            file_name=template.file_name,
            azure_blob_url=template.azure_blob_url,
            file_size_bytes=template.file_size_bytes,
            created_by=actor or "system",
            change_notes=change_notes,
        )
        db.add(version)
