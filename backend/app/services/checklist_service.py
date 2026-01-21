"""
Checklist Service - Business logic for checklist management.
"""

import builtins
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.checklist import ChecklistInstance, ChecklistTemplate
from app.schemas.checklist import (
    ChecklistInstanceCreate,
    ChecklistInstanceUpdateProgress,
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
)

logger = logging.getLogger(__name__)


class ChecklistTemplateService:
    """Service for checklist template CRUD operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        type: str | None = None,
        is_active: bool = True,
    ) -> list[ChecklistTemplate]:
        """
        List checklist templates.

        Args:
            db: Database session
            type: Filter by type (onboarding/offboarding)
            is_active: Filter by active status

        Returns:
            List of templates
        """
        query = select(ChecklistTemplate)

        if type:
            query = query.where(ChecklistTemplate.type == type)

        query = query.where(ChecklistTemplate.is_active == is_active)
        query = query.order_by(ChecklistTemplate.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: UUID) -> ChecklistTemplate | None:
        """Get a template by ID."""
        result = await db.execute(select(ChecklistTemplate).where(ChecklistTemplate.id == str(template_id)))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: ChecklistTemplateCreate) -> ChecklistTemplate:
        """Create a new checklist template."""
        # Convert items to list of dicts
        items_data = [item.model_dump() for item in data.items]

        template = ChecklistTemplate(
            name=data.name,
            description=data.description,
            type=data.type,
            items=items_data,
            is_active=data.is_active,
        )
        db.add(template)
        await db.flush()
        await db.refresh(template)

        logger.info(f"Created checklist template: {template.name} ({template.id})")
        return template

    @staticmethod
    async def update(db: AsyncSession, template_id: UUID, data: ChecklistTemplateUpdate) -> ChecklistTemplate | None:
        """Update a checklist template."""
        template = await ChecklistTemplateService.get_by_id(db, template_id)
        if not template:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Convert items if provided
        if "items" in update_data and update_data["items"]:
            update_data["items"] = [
                item.model_dump() if hasattr(item, "model_dump") else item for item in update_data["items"]
            ]

        for field, value in update_data.items():
            setattr(template, field, value)

        await db.flush()
        await db.refresh(template)

        logger.info(f"Updated checklist template: {template.name} ({template.id})")
        return template

    @staticmethod
    async def deactivate(db: AsyncSession, template_id: UUID) -> ChecklistTemplate | None:
        """Deactivate a checklist template."""
        template = await ChecklistTemplateService.get_by_id(db, template_id)
        if not template:
            return None

        template.is_active = False
        await db.flush()
        await db.refresh(template)

        logger.info(f"Deactivated checklist template: {template.name} ({template.id})")
        return template


class ChecklistInstanceService:
    """Service for checklist instance operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        employee_id: UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[ChecklistInstance], int]:
        """
        List checklist instances with filtering.

        Args:
            db: Database session
            employee_id: Filter by employee
            status: Filter by status
            skip: Offset for pagination
            limit: Max results

        Returns:
            Tuple of (instances, total_count)
        """
        query = select(ChecklistInstance).options(
            selectinload(ChecklistInstance.template), selectinload(ChecklistInstance.employee)
        )
        count_query = select(func.count()).select_from(ChecklistInstance)

        if employee_id:
            query = query.where(ChecklistInstance.employee_id == str(employee_id))
            count_query = count_query.where(ChecklistInstance.employee_id == str(employee_id))

        if status:
            query = query.where(ChecklistInstance.status == status)
            count_query = count_query.where(ChecklistInstance.status == status)

        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute main query
        query = query.order_by(ChecklistInstance.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        instances = list(result.scalars().all())

        return instances, total

    @staticmethod
    async def get_by_id(db: AsyncSession, instance_id: UUID) -> ChecklistInstance | None:
        """Get an instance by ID with related entities."""
        result = await db.execute(
            select(ChecklistInstance)
            .options(selectinload(ChecklistInstance.template), selectinload(ChecklistInstance.employee))
            .where(ChecklistInstance.id == str(instance_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: ChecklistInstanceCreate) -> ChecklistInstance:
        """
        Assign a checklist to an employee.

        Args:
            db: Database session
            data: Instance creation data

        Returns:
            Created instance
        """
        instance = ChecklistInstance(
            template_id=str(data.template_id),
            employee_id=str(data.employee_id),
            due_date=data.due_date,
            status="in_progress",
            items_completed=[],
        )
        db.add(instance)
        await db.flush()
        await db.refresh(instance)

        logger.info(f"Created checklist instance for employee {data.employee_id}")
        return instance

    @staticmethod
    async def update_progress(
        db: AsyncSession, instance_id: UUID, data: ChecklistInstanceUpdateProgress
    ) -> ChecklistInstance | None:
        """
        Update checklist progress.

        Args:
            db: Database session
            instance_id: Instance UUID
            data: Progress update data

        Returns:
            Updated instance or None if not found
        """
        instance = await ChecklistInstanceService.get_by_id(db, instance_id)
        if not instance:
            return None

        instance.items_completed = data.items_completed

        # Check if completed
        if instance.template:
            total_items = len(instance.template.items or [])
            completed_items = len(data.items_completed)

            if completed_items >= total_items:
                instance.status = "completed"
                instance.completed_at = datetime.utcnow()

        await db.flush()
        await db.refresh(instance)

        logger.info(f"Updated checklist progress: {instance.id}")
        return instance

    @staticmethod
    async def cancel(db: AsyncSession, instance_id: UUID) -> ChecklistInstance | None:
        """Cancel a checklist instance."""
        instance = await ChecklistInstanceService.get_by_id(db, instance_id)
        if not instance:
            return None

        instance.status = "cancelled"
        await db.flush()
        await db.refresh(instance)

        logger.info(f"Cancelled checklist instance: {instance.id}")
        return instance

    @staticmethod
    async def get_by_employee(
        db: AsyncSession, employee_id: UUID, *, status: str | None = None
    ) -> builtins.list[ChecklistInstance]:
        """Get all checklists for an employee."""
        query = (
            select(ChecklistInstance)
            .options(selectinload(ChecklistInstance.template))
            .where(ChecklistInstance.employee_id == str(employee_id))
        )

        if status:
            query = query.where(ChecklistInstance.status == status)

        query = query.order_by(ChecklistInstance.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
