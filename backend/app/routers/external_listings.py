"""
External Listings Router - API endpoints for third-party listing management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.external_listing_service import ExternalListingService
from app.schemas.external_listing import (
    ExternalListingCreate,
    ExternalListingUpdate,
    ExternalListingResponse,
    ExternalListingListResponse,
    ExternalListingVerify,
)

router = APIRouter(prefix="/external-listings", tags=["External Listings"])


def _to_response(listing) -> ExternalListingResponse:
    """Convert ExternalListing model to response schema."""
    return ExternalListingResponse(
        id=listing.id,
        office_id=listing.office_id,
        employee_id=listing.employee_id,
        source=listing.source,
        listing_url=listing.listing_url,
        listing_type=listing.listing_type,
        status=listing.status,
        notes=listing.notes,
        last_verified_at=listing.last_verified_at,
        last_verified_by=listing.last_verified_by,
        created_at=listing.created_at,
        updated_at=listing.updated_at,
        source_display_name=listing.source_display_name,
        owner_type=listing.owner_type,
        is_verified=listing.is_verified,
        needs_attention=listing.needs_attention,
    )


@router.get("", response_model=ExternalListingListResponse)
async def list_external_listings(
    office_id: Optional[UUID] = Query(None, description="Filter by office"),
    employee_id: Optional[UUID] = Query(None, description="Filter by employee"),
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all external listings with optional filtering.
    
    Status can be: verified, needs_update, pending_check, removed.
    Source can be: anbudstjenester, finn, nummeropplysning, 1881, gulesider, google, other.
    """
    listings, total = await ExternalListingService.list(
        db,
        office_id=office_id,
        employee_id=employee_id,
        status=status,
        source=source,
        skip=skip,
        limit=limit,
    )
    
    items = [_to_response(l) for l in listings]
    
    return ExternalListingListResponse(items=items, total=total)


@router.post("", response_model=ExternalListingResponse, status_code=201)
async def create_external_listing(
    data: ExternalListingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new external listing.
    
    Either office_id or employee_id must be provided.
    """
    if not data.office_id and not data.employee_id:
        raise HTTPException(
            status_code=400,
            detail="Either office_id or employee_id must be provided"
        )
    
    listing = await ExternalListingService.create(db, data)
    return _to_response(listing)


@router.get("/needing-attention")
async def get_listings_needing_attention(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all listings needing attention.
    
    Returns listings with status 'needs_update' or 'pending_check'.
    """
    listings = await ExternalListingService.get_needing_attention(db)
    return {
        "count": len(listings),
        "listings": [_to_response(l) for l in listings],
    }


@router.get("/{listing_id}", response_model=ExternalListingResponse)
async def get_external_listing(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get an external listing by ID.
    """
    listing = await ExternalListingService.get_by_id(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return _to_response(listing)


@router.put("/{listing_id}", response_model=ExternalListingResponse)
async def update_external_listing(
    listing_id: UUID,
    data: ExternalListingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an external listing.
    
    Only provided fields will be updated.
    """
    listing = await ExternalListingService.update(db, listing_id, data)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return _to_response(listing)


@router.post("/{listing_id}/verify", response_model=ExternalListingResponse)
async def verify_external_listing(
    listing_id: UUID,
    data: ExternalListingVerify,
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a listing as verified.
    
    Updates the status and records verification timestamp.
    """
    listing = await ExternalListingService.verify(
        db,
        listing_id,
        status=data.status,
        verified_by="system",  # TODO: Get from auth
        notes=data.notes,
    )
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return _to_response(listing)


@router.delete("/{listing_id}", status_code=204)
async def delete_external_listing(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an external listing.
    """
    success = await ExternalListingService.delete(db, listing_id)
    if not success:
        raise HTTPException(status_code=404, detail="Listing not found")
