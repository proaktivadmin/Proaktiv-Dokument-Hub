"""
Territories Router - API endpoints for postal codes and office territories.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
import csv
import io

from app.database import get_db
from app.services.territory_service import PostalCodeService, OfficeTerritoryService
from app.models.office_territory import OfficeTerritory
from app.services.office_service import OfficeService
from app.schemas.territory import (
    PostalCodeResponse,
    PostalCodeSyncResult,
    OfficeTerritoryCreate,
    OfficeTerritoryUpdate,
    OfficeTerritoryResponse,
    OfficeTerritoryWithDetails,
    OfficeTerritoryListResponse,
    TerritoryMapData,
    TerritoryImportResult,
    BlacklistEntry,
    OfficeMinimalForTerritory,
)

router = APIRouter(tags=["Territories"])


def _postal_code_to_response(pc) -> PostalCodeResponse:
    """Convert PostalCode model to response schema."""
    return PostalCodeResponse(
        postal_code=pc.postal_code,
        postal_name=pc.postal_name,
        municipality_code=pc.municipality_code,
        municipality_name=pc.municipality_name,
        category=pc.category,
        created_at=pc.created_at,
        updated_at=pc.updated_at,
        full_location=pc.full_location,
        category_name=pc.category_name,
        is_street_address=pc.is_street_address,
    )


def _territory_to_response(t) -> OfficeTerritoryWithDetails:
    """Convert OfficeTerritory model to response schema with details."""
    return OfficeTerritoryWithDetails(
        id=t.id,
        office_id=t.office_id,
        postal_code=t.postal_code,
        source=t.source,
        priority=t.priority,
        is_blacklisted=t.is_blacklisted,
        valid_from=t.valid_from,
        valid_to=t.valid_to,
        created_at=t.created_at,
        updated_at=t.updated_at,
        is_active=t.is_active,
        source_display_name=t.source_display_name,
        office=OfficeMinimalForTerritory(
            id=t.office.id,
            name=t.office.name,
            short_code=t.office.short_code,
            color=t.office.color,
        ) if t.office else None,
        postal_info=_postal_code_to_response(t.postal_code_info) if t.postal_code_info else None,
    )


# =============================================================================
# Postal Code Endpoints
# =============================================================================

@router.get("/postal-codes", response_model=List[PostalCodeResponse])
async def list_postal_codes(
    db: AsyncSession = Depends(get_db),
):
    """
    List all postal codes.
    
    Returns all Norwegian postal codes from the database.
    Run /postal-codes/sync to populate from Bring registry.
    """
    postal_codes = await PostalCodeService.list(db)
    return [_postal_code_to_response(pc) for pc in postal_codes]


@router.post("/postal-codes/sync", response_model=PostalCodeSyncResult)
async def sync_postal_codes(
    db: AsyncSession = Depends(get_db),
):
    """
    Sync postal codes from Bring Postnummerregister.
    
    Downloads and upserts all Norwegian postal codes.
    """
    result = await PostalCodeService.sync_from_bring(db)
    return PostalCodeSyncResult(**result)


@router.get("/postal-codes/{postal_code}", response_model=PostalCodeResponse)
async def get_postal_code(
    postal_code: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a postal code by its code.
    """
    pc = await PostalCodeService.get_by_code(db, postal_code)
    if not pc:
        raise HTTPException(status_code=404, detail="Postal code not found")
    
    return _postal_code_to_response(pc)


# =============================================================================
# Territory Endpoints
# =============================================================================

@router.get("/territories", response_model=OfficeTerritoryListResponse)
async def list_territories(
    office_id: Optional[UUID] = Query(None, description="Filter by office"),
    source: Optional[str] = Query(None, description="Filter by source"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all territory assignments.
    
    Source can be: vitec_next, finn, anbudstjenester, homepage, other.
    """
    territories, total = await OfficeTerritoryService.list(
        db,
        office_id=office_id,
        source=source,
        skip=skip,
        limit=limit,
    )
    
    items = [_territory_to_response(t) for t in territories]
    
    return OfficeTerritoryListResponse(items=items, total=total)


@router.get("/territories/map", response_model=TerritoryMapData)
async def get_map_data(
    layer: Optional[List[str]] = Query(None, description="Source layers to include"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get GeoJSON data for territory map.
    
    Returns feature collection with territory properties.
    Note: Geometry data is a placeholder - actual polygons would need
    to be sourced from a postal code geometry dataset.
    """
    return await OfficeTerritoryService.get_map_data(db, layers=layer)


@router.get("/territories/layers")
async def get_available_layers(
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of available source layers.
    """
    sources = await OfficeTerritoryService.get_available_sources(db)
    return {"layers": sources}


@router.get("/territories/stats")
async def get_territory_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get territory summary stats for dashboard cards.
    """
    total = await db.scalar(
        select(func.count()).select_from(OfficeTerritory)
    ) or 0

    by_source = {
        "vitec_next": 0,
        "finn": 0,
        "anbudstjenester": 0,
        "homepage": 0,
        "other": 0,
    }
    by_source_result = await db.execute(
        select(OfficeTerritory.source, func.count())
        .group_by(OfficeTerritory.source)
    )
    for source, count in by_source_result.all():
        by_source[source] = count

    offices_with_territories = await db.scalar(
        select(func.count(func.distinct(OfficeTerritory.office_id)))
    ) or 0

    blacklisted_count = await db.scalar(
        select(func.count())
        .select_from(OfficeTerritory)
        .where(OfficeTerritory.is_blacklisted == True)
    ) or 0

    return {
        "total_territories": total,
        "by_source": by_source,
        "offices_with_territories": offices_with_territories,
        "blacklisted_count": blacklisted_count,
    }


@router.post("/territories", response_model=OfficeTerritoryWithDetails, status_code=201)
async def create_territory(
    data: OfficeTerritoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new territory assignment.
    """
    # Verify office exists
    office = await OfficeService.get_by_id(db, data.office_id)
    if not office:
        raise HTTPException(status_code=400, detail="Office not found")
    
    # Verify postal code exists
    pc = await PostalCodeService.get_by_code(db, data.postal_code)
    if not pc:
        raise HTTPException(status_code=400, detail="Postal code not found")
    
    territory = await OfficeTerritoryService.create(db, data)
    
    # Reload with relationships
    territory = await OfficeTerritoryService.get_by_id(db, territory.id)
    return _territory_to_response(territory)


@router.put("/territories/{territory_id}", response_model=OfficeTerritoryWithDetails)
async def update_territory(
    territory_id: UUID,
    data: OfficeTerritoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a territory assignment.
    """
    territory = await OfficeTerritoryService.update(db, territory_id, data)
    if not territory:
        raise HTTPException(status_code=404, detail="Territory not found")
    
    # Reload with relationships
    territory = await OfficeTerritoryService.get_by_id(db, territory.id)
    return _territory_to_response(territory)


@router.delete("/territories/{territory_id}", status_code=204)
async def delete_territory(
    territory_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a territory assignment.
    """
    success = await OfficeTerritoryService.delete(db, territory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Territory not found")


# =============================================================================
# Blacklist Endpoints
# =============================================================================

@router.get("/territories/blacklist")
async def get_blacklist(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all blacklisted postal codes.
    """
    postal_codes = await OfficeTerritoryService.get_blacklist(db)
    return {"postal_codes": postal_codes}


@router.post("/territories/blacklist", status_code=201)
async def add_to_blacklist(
    data: BlacklistEntry,
    office_id: UUID = Query(..., description="Office to blacklist for"),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a postal code to blacklist for an office.
    """
    # Verify office exists
    office = await OfficeService.get_by_id(db, office_id)
    if not office:
        raise HTTPException(status_code=400, detail="Office not found")
    
    # Verify postal code exists
    pc = await PostalCodeService.get_by_code(db, data.postal_code)
    if not pc:
        raise HTTPException(status_code=400, detail="Postal code not found")
    
    territory = await OfficeTerritoryService.add_to_blacklist(db, data.postal_code, office_id)
    return {"message": f"Added {data.postal_code} to blacklist"}


# =============================================================================
# Import Endpoints
# =============================================================================

@router.post("/territories/import", response_model=TerritoryImportResult)
async def import_territories(
    file: UploadFile = File(...),
    office_id: UUID = Query(..., description="Office to assign territories to"),
    source: str = Query("vitec_next", description="Source identifier"),
    db: AsyncSession = Depends(get_db),
):
    """
    Import territories from CSV file.
    
    Expected CSV format:
    postal_code,priority
    0001,1
    0002,2
    """
    # Verify office exists
    office = await OfficeService.get_by_id(db, office_id)
    if not office:
        raise HTTPException(status_code=400, detail="Office not found")
    
    # Parse CSV
    content = await file.read()
    try:
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        data = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")
    
    result = await OfficeTerritoryService.import_from_csv(db, data, office_id, source)
    return TerritoryImportResult(**result)
