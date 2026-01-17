"""
ExternalListing Service - Business logic for third-party listing management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging

from app.models.external_listing import ExternalListing
from app.schemas.external_listing import ExternalListingCreate, ExternalListingUpdate

logger = logging.getLogger(__name__)


class ExternalListingService:
    """Service for external listing CRUD operations."""
    
    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        office_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[ExternalListing], int]:
        """
        List external listings with filtering.
        
        Args:
            db: Database session
            office_id: Filter by office
            employee_id: Filter by employee
            status: Filter by status
            source: Filter by source
            skip: Offset for pagination
            limit: Max results
            
        Returns:
            Tuple of (listings, total_count)
        """
        query = select(ExternalListing).options(
            selectinload(ExternalListing.office),
            selectinload(ExternalListing.employee)
        )
        count_query = select(func.count()).select_from(ExternalListing)
        
        if office_id:
            query = query.where(ExternalListing.office_id == str(office_id))
            count_query = count_query.where(ExternalListing.office_id == str(office_id))
        
        if employee_id:
            query = query.where(ExternalListing.employee_id == str(employee_id))
            count_query = count_query.where(ExternalListing.employee_id == str(employee_id))
        
        if status:
            query = query.where(ExternalListing.status == status)
            count_query = count_query.where(ExternalListing.status == status)
        
        if source:
            query = query.where(ExternalListing.source == source)
            count_query = count_query.where(ExternalListing.source == source)
        
        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Execute main query
        query = query.order_by(ExternalListing.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        listings = list(result.scalars().all())
        
        return listings, total
    
    @staticmethod
    async def get_by_id(db: AsyncSession, listing_id: UUID) -> Optional[ExternalListing]:
        """Get a listing by ID."""
        result = await db.execute(
            select(ExternalListing)
            .options(
                selectinload(ExternalListing.office),
                selectinload(ExternalListing.employee)
            )
            .where(ExternalListing.id == str(listing_id))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, data: ExternalListingCreate) -> ExternalListing:
        """Create a new external listing."""
        listing = ExternalListing(
            office_id=str(data.office_id) if data.office_id else None,
            employee_id=str(data.employee_id) if data.employee_id else None,
            source=data.source,
            listing_url=data.listing_url,
            listing_type=data.listing_type,
            status=data.status,
            notes=data.notes,
        )
        db.add(listing)
        await db.flush()
        await db.refresh(listing)
        
        logger.info(f"Created external listing: {listing.source} ({listing.id})")
        return listing
    
    @staticmethod
    async def update(
        db: AsyncSession,
        listing_id: UUID,
        data: ExternalListingUpdate
    ) -> Optional[ExternalListing]:
        """Update an external listing."""
        listing = await ExternalListingService.get_by_id(db, listing_id)
        if not listing:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(listing, field, value)
        
        await db.flush()
        await db.refresh(listing)
        
        logger.info(f"Updated external listing: {listing.id}")
        return listing
    
    @staticmethod
    async def verify(
        db: AsyncSession,
        listing_id: UUID,
        *,
        status: str = "verified",
        verified_by: str,
        notes: Optional[str] = None
    ) -> Optional[ExternalListing]:
        """
        Mark a listing as verified.
        
        Args:
            db: Database session
            listing_id: Listing UUID
            status: New status (default: verified)
            verified_by: User who verified
            notes: Optional verification notes
            
        Returns:
            Updated listing or None if not found
        """
        listing = await ExternalListingService.get_by_id(db, listing_id)
        if not listing:
            return None
        
        listing.status = status
        listing.last_verified_at = datetime.utcnow()
        listing.last_verified_by = verified_by
        if notes:
            listing.notes = notes
        
        await db.flush()
        await db.refresh(listing)
        
        logger.info(f"Verified external listing: {listing.id} -> {status}")
        return listing
    
    @staticmethod
    async def delete(db: AsyncSession, listing_id: UUID) -> bool:
        """Delete an external listing."""
        listing = await ExternalListingService.get_by_id(db, listing_id)
        if not listing:
            return False
        
        await db.delete(listing)
        await db.flush()
        
        logger.info(f"Deleted external listing: {listing_id}")
        return True
    
    @staticmethod
    async def get_by_office(
        db: AsyncSession,
        office_id: UUID,
        *,
        status: Optional[str] = None
    ) -> List[ExternalListing]:
        """Get all listings for an office."""
        query = select(ExternalListing).where(
            ExternalListing.office_id == str(office_id)
        )
        
        if status:
            query = query.where(ExternalListing.status == status)
        
        query = query.order_by(ExternalListing.source)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_employee(
        db: AsyncSession,
        employee_id: UUID,
        *,
        status: Optional[str] = None
    ) -> List[ExternalListing]:
        """Get all listings for an employee."""
        query = select(ExternalListing).where(
            ExternalListing.employee_id == str(employee_id)
        )
        
        if status:
            query = query.where(ExternalListing.status == status)
        
        query = query.order_by(ExternalListing.source)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_needing_attention(db: AsyncSession) -> List[ExternalListing]:
        """Get all listings needing attention (needs_update or pending_check)."""
        result = await db.execute(
            select(ExternalListing)
            .options(
                selectinload(ExternalListing.office),
                selectinload(ExternalListing.employee)
            )
            .where(ExternalListing.status.in_(["needs_update", "pending_check"]))
            .order_by(ExternalListing.updated_at.asc())
        )
        return list(result.scalars().all())
