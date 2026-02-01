"""
Signature Override Service — CRUD for employee signature field overrides.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.signature_override import SignatureOverride
from app.schemas.signature_override import SignatureOverrideUpdate

logger = logging.getLogger(__name__)


class SignatureOverrideService:
    """Service for managing per-employee signature overrides."""

    @staticmethod
    async def get_by_employee_id(db: AsyncSession, employee_id: UUID) -> SignatureOverride | None:
        """Fetch override record for an employee, or None if no overrides exist."""
        result = await db.execute(
            select(SignatureOverride).where(SignatureOverride.employee_id == str(employee_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert(
        db: AsyncSession, employee_id: UUID, data: SignatureOverrideUpdate
    ) -> SignatureOverride:
        """Create or update signature overrides for an employee."""
        override = await SignatureOverrideService.get_by_employee_id(db, employee_id)

        if override:
            # Update existing override
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(override, field, value)
        else:
            # Create new override
            override = SignatureOverride(
                employee_id=str(employee_id),
                **data.model_dump(exclude_unset=True),
            )
            db.add(override)

        await db.commit()
        await db.refresh(override)
        return override

    @staticmethod
    async def delete(db: AsyncSession, employee_id: UUID) -> bool:
        """Remove all overrides for an employee (reset to original)."""
        override = await SignatureOverrideService.get_by_employee_id(db, employee_id)
        if not override:
            return False
        await db.delete(override)
        await db.commit()
        return True

    @staticmethod
    def to_dict(override: SignatureOverride | None) -> dict[str, str | None] | None:
        """Convert override to a dict for use in template rendering. Returns None if no overrides."""
        if not override:
            return None
        return {
            "display_name": override.display_name,
            "job_title": override.job_title,
            "mobile_phone": override.mobile_phone,
            "email": override.email,
            "office_name": override.office_name,
            "facebook_url": override.facebook_url,
            "instagram_url": override.instagram_url,
            "linkedin_url": override.linkedin_url,
            "employee_url": override.employee_url,
        }
