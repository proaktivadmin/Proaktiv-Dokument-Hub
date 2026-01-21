"""
Sync Router - API endpoints for Vitec sync review.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.sync import SyncCommitResult, SyncDecisionUpdate, SyncPreview
from app.services.sync_commit_service import SyncCommitService
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


@router.patch("/sessions/{session_id}/decisions")
async def update_decision(
    session_id: UUID,
    data: SyncDecisionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a decision for a single field in a session.
    """
    service = SyncCommitService()
    await service.update_decision(db, session_id, data)
    return {"success": True}


@router.post("/sessions/{session_id}/commit", response_model=SyncCommitResult)
async def commit_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Apply approved changes from a sync session.
    """
    service = SyncCommitService()
    return await service.commit_session(db, session_id)
