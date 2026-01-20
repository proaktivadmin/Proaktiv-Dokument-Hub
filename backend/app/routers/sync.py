"""
Sync Router - API endpoints for Vitec sync review.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.sync import SyncPreview
from app.services.sync_preview_service import SyncPreviewService

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.post("/preview", response_model=SyncPreview)
async def create_preview(
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a sync preview and create a review session.
    """
    service = SyncPreviewService()
    return await service.generate_preview(db)


@router.get("/sessions/{session_id}", response_model=SyncPreview)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch an existing sync preview session.
    """
    service = SyncPreviewService()
    return await service.get_session(db, session_id)


@router.delete("/sessions/{session_id}")
async def cancel_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a sync session.
    """
    service = SyncPreviewService()
    await service.cancel_session(db, session_id)
    return {"success": True}
