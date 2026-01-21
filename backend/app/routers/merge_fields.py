"""
Merge Fields API Routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.merge_field import (
    MergeFieldCreate,
    MergeFieldDiscoveryResult,
    MergeFieldListResponse,
    MergeFieldResponse,
    MergeFieldUpdate,
)
from app.services.merge_field_service import MergeFieldService

router = APIRouter(prefix="/merge-fields", tags=["Merge Fields"])


@router.get("", response_model=MergeFieldListResponse)
async def list_merge_fields(
    db: AsyncSession = Depends(get_db),
    category: str | None = Query(None),
    search: str | None = Query(None),
    data_type: str | None = Query(None),
    is_iterable: bool | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
):
    """List all merge fields with optional filters."""
    fields, total = await MergeFieldService.get_list(
        db, category=category, search=search, data_type=data_type, is_iterable=is_iterable, page=page, per_page=per_page
    )

    return MergeFieldListResponse(
        merge_fields=[MergeFieldResponse.model_validate(f) for f in fields],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page if total > 0 else 0,
    )


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all unique categories."""
    categories = await MergeFieldService.get_categories(db)
    return {"categories": categories}


@router.get("/autocomplete")
async def autocomplete(
    db: AsyncSession = Depends(get_db), q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)
):
    """Search merge fields for autocomplete suggestions."""
    fields = await MergeFieldService.search_autocomplete(db, q, limit)
    return [MergeFieldResponse.model_validate(f) for f in fields]


@router.post("/scan", response_model=MergeFieldDiscoveryResult)
async def trigger_discovery(db: AsyncSession = Depends(get_db), create_missing: bool = Query(True)):
    """Scan all templates and discover merge fields."""
    result = await MergeFieldService.discover_all(db, create_missing=create_missing)
    return MergeFieldDiscoveryResult(**result)


@router.get("/{field_id}", response_model=MergeFieldResponse)
async def get_merge_field(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a merge field by ID."""
    field = await MergeFieldService.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Merge field not found")
    return MergeFieldResponse.model_validate(field)


@router.post("", response_model=MergeFieldResponse, status_code=201)
async def create_merge_field(body: MergeFieldCreate, db: AsyncSession = Depends(get_db)):
    """Create a new merge field."""
    existing = await MergeFieldService.get_by_path(db, body.path)
    if existing:
        raise HTTPException(status_code=409, detail=f"Path '{body.path}' already exists")

    field = await MergeFieldService.create(db, **body.model_dump())
    return MergeFieldResponse.model_validate(field)


@router.put("/{field_id}", response_model=MergeFieldResponse)
async def update_merge_field(field_id: UUID, body: MergeFieldUpdate, db: AsyncSession = Depends(get_db)):
    """Update a merge field."""
    field = await MergeFieldService.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Merge field not found")

    field = await MergeFieldService.update(db, field, **body.model_dump(exclude_unset=True))
    return MergeFieldResponse.model_validate(field)


@router.delete("/{field_id}", status_code=204)
async def delete_merge_field(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a merge field."""
    field = await MergeFieldService.get_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Merge field not found")

    await MergeFieldService.delete(db, field)
    return None
