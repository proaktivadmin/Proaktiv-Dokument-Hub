"""
Notification Service - Business logic for notifications.
"""

import logging
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.notification import Notification
from app.models.office import Office
from app.schemas.notification import NotificationCreate

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification CRUD operations."""

    @staticmethod
    async def create(db: AsyncSession, data: NotificationCreate) -> Notification:
        """
        Create a notification entry.
        """
        notification = Notification(
            type=data.type,
            entity_type=data.entity_type,
            entity_id=str(data.entity_id) if data.entity_id else None,
            title=data.title,
            message=data.message,
            severity=data.severity,
            metadata_json=data.metadata,
        )
        db.add(notification)
        await db.flush()
        await db.refresh(notification)

        logger.info("Created notification: %s (%s)", notification.type, notification.id)
        return notification

    @staticmethod
    async def get_all(
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int, int]:
        """
        Get notifications with pagination and optional unread filter.

        Returns:
            Tuple of (items, total_count, unread_count)
        """
        base_query = select(Notification)
        count_query = select(func.count()).select_from(Notification)

        if unread_only:
            base_query = base_query.where(Notification.is_read.is_(False))
            count_query = count_query.where(Notification.is_read.is_(False))

        base_query = base_query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(base_query)
        items = list(result.scalars().all())

        total = await db.scalar(count_query) or 0
        unread_count = await NotificationService.get_unread_count(db)

        return items, total, unread_count

    @staticmethod
    async def get_unread_count(db: AsyncSession) -> int:
        """
        Get total unread notification count.
        """
        count_query = select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))
        return await db.scalar(count_query) or 0

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification_id: UUID) -> Notification | None:
        """
        Mark a notification as read.
        """
        result = await db.execute(select(Notification).where(Notification.id == str(notification_id)))
        notification = result.scalar_one_or_none()
        if not notification:
            return None

        if not notification.is_read:
            notification.is_read = True
            await db.flush()
            await db.refresh(notification)

        return notification

    @staticmethod
    async def mark_all_as_read(db: AsyncSession) -> int:
        """
        Mark all notifications as read.

        Returns:
            Count of notifications marked as read.
        """
        count_query = select(func.count()).select_from(Notification).where(Notification.is_read.is_(False))
        count = await db.scalar(count_query) or 0
        if count == 0:
            return 0

        await db.execute(update(Notification).where(Notification.is_read.is_(False)).values(is_read=True))
        return count

    @staticmethod
    async def delete(db: AsyncSession, notification_id: UUID) -> bool:
        """
        Delete a single notification.
        """
        result = await db.execute(select(Notification).where(Notification.id == str(notification_id)))
        notification = result.scalar_one_or_none()
        if not notification:
            return False

        await db.delete(notification)
        await db.flush()
        return True

    @staticmethod
    async def clear_all(db: AsyncSession) -> int:
        """
        Delete all notifications.

        Returns:
            Count of notifications deleted.
        """
        count_query = select(func.count()).select_from(Notification)
        count = await db.scalar(count_query) or 0
        if count == 0:
            return 0

        await db.execute(delete(Notification))
        return count

    # =============================================================================
    # Helper Methods for Sync Integration
    # =============================================================================

    @staticmethod
    def _employee_metadata(employee: Employee) -> dict[str, object]:
        return {
            "employee_id": str(employee.id),
            "employee_name": employee.full_name,
            "office_id": str(employee.office_id) if employee.office_id else None,
            "email": employee.email,
        }

    @staticmethod
    def _office_metadata(office: Office) -> dict[str, object]:
        return {
            "office_id": str(office.id),
            "office_name": office.name,
            "short_code": office.short_code,
            "vitec_department_id": office.vitec_department_id,
        }

    @staticmethod
    async def notify_employee_added(db: AsyncSession, employee: Employee) -> Notification:
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="employee_added",
                entity_type="employee",
                entity_id=employee.id,
                title="Ny ansatt lagt til",
                message=f"{employee.full_name} ble lagt til.",
                severity="info",
                metadata=NotificationService._employee_metadata(employee),
            ),
        )

    @staticmethod
    async def notify_employee_updated(db: AsyncSession, employee: Employee, changed_fields: list[str]) -> Notification:
        fields = [field for field in changed_fields if field]
        fields_text = ", ".join(fields)
        message = (
            f"{employee.full_name} ble oppdatert ({fields_text})."
            if fields_text
            else f"{employee.full_name} ble oppdatert."
        )
        metadata = NotificationService._employee_metadata(employee)
        metadata["changed_fields"] = fields
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="employee_updated",
                entity_type="employee",
                entity_id=employee.id,
                title="Ansatt oppdatert",
                message=message,
                severity="info",
                metadata=metadata,
            ),
        )

    @staticmethod
    async def notify_employee_removed(db: AsyncSession, employee: Employee) -> Notification:
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="employee_removed",
                entity_type="employee",
                entity_id=employee.id,
                title="Ansatt fjernet",
                message=f"{employee.full_name} ble fjernet.",
                severity="warning",
                metadata=NotificationService._employee_metadata(employee),
            ),
        )

    @staticmethod
    async def notify_office_added(db: AsyncSession, office: Office) -> Notification:
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="office_added",
                entity_type="office",
                entity_id=office.id,
                title="Nytt kontor lagt til",
                message=f"{office.name} ble lagt til.",
                severity="info",
                metadata=NotificationService._office_metadata(office),
            ),
        )

    @staticmethod
    async def notify_office_updated(db: AsyncSession, office: Office, changed_fields: list[str]) -> Notification:
        fields = [field for field in changed_fields if field]
        fields_text = ", ".join(fields)
        message = f"{office.name} ble oppdatert ({fields_text})." if fields_text else f"{office.name} ble oppdatert."
        metadata = NotificationService._office_metadata(office)
        metadata["changed_fields"] = fields
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="office_updated",
                entity_type="office",
                entity_id=office.id,
                title="Kontor oppdatert",
                message=message,
                severity="info",
                metadata=metadata,
            ),
        )

    @staticmethod
    async def notify_office_removed(db: AsyncSession, office: Office) -> Notification:
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="office_removed",
                entity_type="office",
                entity_id=office.id,
                title="Kontor fjernet",
                message=f"{office.name} ble fjernet.",
                severity="warning",
                metadata=NotificationService._office_metadata(office),
            ),
        )

    @staticmethod
    async def notify_upn_mismatch(
        db: AsyncSession, employee: Employee, expected_upn: str, actual_upn: str
    ) -> Notification:
        metadata = NotificationService._employee_metadata(employee)
        metadata.update({"expected_upn": expected_upn, "actual_upn": actual_upn})
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="upn_mismatch",
                entity_type="employee",
                entity_id=employee.id,
                title="UPN-avvik oppdaget",
                message=(f"{employee.full_name} har UPN {actual_upn}, men forventet {expected_upn}."),
                severity="error",
                metadata=metadata,
            ),
        )

    @staticmethod
    async def notify_sync_error(db: AsyncSession, operation: str, error: str) -> Notification:
        metadata = {"operation": operation, "error": error}
        return await NotificationService.create(
            db,
            NotificationCreate(
                type="sync_error",
                entity_type="sync",
                entity_id=None,
                title="Synkroniseringsfeil",
                message=f"{operation}: {error}",
                severity="error",
                metadata=metadata,
            ),
        )
