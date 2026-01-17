"""
Dashboard API Routes
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.services.inventory_service import InventoryService
from app.schemas.template_settings import DashboardStatsResponse
from pydantic import BaseModel


class InventorySyncStats(BaseModel):
    """Schema for inventory sync statistics."""
    total_vitec_templates: int
    total_local_templates: int
    synced: int
    missing: int
    modified: int
    local_only: int
    sync_percentage: float


class MissingTemplateInfo(BaseModel):
    """Schema for missing template info."""
    id: str
    vitec_name: str
    vitec_type: str
    vitec_phase: str | None
    vitec_category: str | None
    vitec_channel: str | None
    description: str | None


class InventoryStatsResponse(BaseModel):
    """Full inventory stats response."""
    stats: InventorySyncStats
    missing_templates: List[MissingTemplateInfo]


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics."""
    stats = await DashboardService.get_stats(db)
    return DashboardStatsResponse(**stats)


@router.get("/inventory", response_model=InventoryStatsResponse)
async def get_inventory_stats(
    db: AsyncSession = Depends(get_db),
    missing_limit: int = Query(5, ge=1, le=50, description="Max missing templates to return")
):
    """
    Get Vitec template inventory sync statistics.
    
    Returns overview of how many templates are synced, missing, or modified.
    """
    sync_stats = await InventoryService.get_sync_stats(db)
    missing_templates = await InventoryService.get_missing_templates(db, limit=missing_limit)
    
    return InventoryStatsResponse(
        stats=InventorySyncStats(**sync_stats),
        missing_templates=[MissingTemplateInfo(**t) for t in missing_templates]
    )


@router.get("/inventory/by-phase", response_model=Dict[str, Dict[str, int]])
async def get_inventory_by_phase(
    db: AsyncSession = Depends(get_db)
):
    """
    Get inventory stats grouped by phase.
    
    Returns dict with phase names as keys and status counts as values.
    """
    return await InventoryService.get_by_phase(db)
