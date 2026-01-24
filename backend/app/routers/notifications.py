"""
Notifications Router - API endpoints for notification management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=200, description="Max results"),
    unread_only: bool = Query(False, description="Only include unread notifications"),
    db: AsyncSession = Depends(get_db),
):
    """
    List notifications with pagination and optional unread filter.
    """
    items, total, unread_count = await NotificationService.get_all(db, skip=skip, limit=limit, unread_only=unread_only)
    return NotificationListResponse(items=items, total=total, unread_count=unread_count)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(db: AsyncSession = Depends(get_db)):
    """
    Get total unread notification count.
    """
    count = await NotificationService.get_unread_count(db)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a notification as read.
    """
    notification = await NotificationService.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.post("/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db)):
    """
    Mark all notifications as read.
    """
    count = await NotificationService.mark_all_as_read(db)
    return {"count": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a single notification.
    """
    deleted = await NotificationService.delete(db, notification_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}


@router.post("/clear")
async def clear_all_notifications(db: AsyncSession = Depends(get_db)):
    """
    Delete all notifications.
    """
    count = await NotificationService.clear_all(db)
    return {"count": count}
