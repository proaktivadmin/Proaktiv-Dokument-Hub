"""
Offices Router - API endpoints for office management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.office import (
    OfficeCreate,
    OfficeListResponse,
    OfficeSyncResult,
    OfficeUpdate,
    OfficeWithStats,
)
from app.services.office_service import OfficeService

router = APIRouter(prefix="/offices", tags=["Offices"])


@router.get("", response_model=OfficeListResponse)
async def list_offices(
    city: str | None = Query(None, description="Filter by city"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all offices with optional filtering.

    Returns offices with computed statistics (employee counts, territory count).
    """
    offices, total = await OfficeService.list(
        db,
        city=city,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )

    items = [OfficeService.to_response_with_stats(office) for office in offices]

    return OfficeListResponse(items=items, total=total)


@router.post("/sync", response_model=OfficeSyncResult)
async def sync_offices(
    db: AsyncSession = Depends(get_db),
):
    """
    Sync offices from Vitec Hub (Departments endpoint).
    """
    result = await OfficeService.sync_from_hub(db)
    return OfficeSyncResult(**result)


@router.post("", response_model=OfficeWithStats, status_code=201)
async def create_office(
    data: OfficeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new office.

    The short_code must be unique and will be uppercased.
    """
    # Check for duplicate short_code
    existing = await OfficeService.get_by_short_code(db, data.short_code)
    if existing:
        raise HTTPException(status_code=400, detail=f"Office with short code '{data.short_code}' already exists")

    office = await OfficeService.create(db, data)
    return OfficeService.to_response_with_stats(office)


@router.get("/{office_id}", response_model=OfficeWithStats)
async def get_office(
    office_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get an office by ID.

    Returns the office with computed statistics.
    """
    office = await OfficeService.get_by_id(db, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    return OfficeService.to_response_with_stats(office)


@router.put("/{office_id}", response_model=OfficeWithStats)
async def update_office(
    office_id: UUID,
    data: OfficeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an office.

    Only provided fields will be updated.
    """
    # Check for duplicate short_code if changing
    if data.short_code:
        existing = await OfficeService.get_by_short_code(db, data.short_code)
        if existing and str(existing.id) != str(office_id):
            raise HTTPException(status_code=400, detail=f"Office with short code '{data.short_code}' already exists")

    office = await OfficeService.update(db, office_id, data)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    return OfficeService.to_response_with_stats(office)


@router.delete("/{office_id}", response_model=OfficeWithStats)
async def deactivate_office(
    office_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate an office (soft delete).

    Sets is_active to False. Office data is preserved.
    """
    office = await OfficeService.deactivate(db, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    return OfficeService.to_response_with_stats(office)


@router.get("/{office_id}/stats")
async def get_office_stats(
    office_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics for an office.

    Returns employee counts and territory count.
    """
    office = await OfficeService.get_by_id(db, office_id)
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    stats = await OfficeService.get_stats(db, office_id)
    return {"office_id": str(office_id), **stats}
