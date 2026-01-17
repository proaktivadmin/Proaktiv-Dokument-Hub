"""
LayoutPartialVersion Service - Business logic for layout partial versioning.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
import logging

from app.models.layout_partial import LayoutPartial
from app.models.layout_partial_version import LayoutPartialVersion, LayoutPartialDefault
from app.schemas.layout_partial_version import (
    LayoutPartialVersionCreate,
    LayoutPartialDefaultCreate,
    LayoutPartialDefaultUpdate,
)

logger = logging.getLogger(__name__)


class LayoutPartialVersionService:
    """Service for layout partial version operations."""
    
    @staticmethod
    async def list_versions(
        db: AsyncSession,
        partial_id: UUID
    ) -> tuple[List[LayoutPartialVersion], int]:
        """
        List all versions for a layout partial.
        
        Args:
            db: Database session
            partial_id: Layout partial UUID
            
        Returns:
            Tuple of (versions, current_version_number)
        """
        # Get the partial to find current version
        partial_result = await db.execute(
            select(LayoutPartial).where(LayoutPartial.id == str(partial_id))
        )
        partial = partial_result.scalar_one_or_none()
        
        current_version = 1
        if partial and partial.versions:
            current_version = max(v.version_number for v in partial.versions)
        
        result = await db.execute(
            select(LayoutPartialVersion)
            .where(LayoutPartialVersion.partial_id == str(partial_id))
            .order_by(LayoutPartialVersion.version_number.desc())
        )
        versions = list(result.scalars().all())
        
        return versions, current_version
    
    @staticmethod
    async def get_version(
        db: AsyncSession,
        partial_id: UUID,
        version_number: int
    ) -> Optional[LayoutPartialVersion]:
        """Get a specific version of a layout partial."""
        result = await db.execute(
            select(LayoutPartialVersion)
            .where(LayoutPartialVersion.partial_id == str(partial_id))
            .where(LayoutPartialVersion.version_number == version_number)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_version(
        db: AsyncSession,
        partial_id: UUID,
        data: LayoutPartialVersionCreate
    ) -> LayoutPartialVersion:
        """
        Create a new version of a layout partial.
        
        Args:
            db: Database session
            partial_id: Layout partial UUID
            data: Version data
            
        Returns:
            Created version
        """
        # Get current max version
        result = await db.execute(
            select(func.max(LayoutPartialVersion.version_number))
            .where(LayoutPartialVersion.partial_id == str(partial_id))
        )
        max_version = result.scalar() or 0
        
        version = LayoutPartialVersion(
            partial_id=str(partial_id),
            version_number=max_version + 1,
            html_content=data.html_content,
            change_notes=data.change_notes,
            created_by=data.created_by,
        )
        db.add(version)
        await db.flush()
        await db.refresh(version)
        
        logger.info(f"Created version {version.version_number} for partial {partial_id}")
        return version
    
    @staticmethod
    async def revert_to_version(
        db: AsyncSession,
        partial_id: UUID,
        version_number: int,
        *,
        reverted_by: str
    ) -> dict:
        """
        Revert a layout partial to a previous version.
        
        This creates a new version with the content from the specified version.
        
        Args:
            db: Database session
            partial_id: Layout partial UUID
            version_number: Version to revert to
            reverted_by: User performing the revert
            
        Returns:
            Dict with revert details
        """
        # Get the version to revert to
        version = await LayoutPartialVersionService.get_version(
            db, partial_id, version_number
        )
        if not version:
            raise ValueError(f"Version {version_number} not found")
        
        # Get the partial
        partial_result = await db.execute(
            select(LayoutPartial).where(LayoutPartial.id == str(partial_id))
        )
        partial = partial_result.scalar_one_or_none()
        if not partial:
            raise ValueError(f"Layout partial {partial_id} not found")
        
        # Create snapshot of current content
        current_max = await db.execute(
            select(func.max(LayoutPartialVersion.version_number))
            .where(LayoutPartialVersion.partial_id == str(partial_id))
        )
        current_version_num = current_max.scalar() or 0
        
        # Create new version with reverted content
        new_version = LayoutPartialVersion(
            partial_id=str(partial_id),
            version_number=current_version_num + 1,
            html_content=version.html_content,
            change_notes=f"Reverted from version {version_number}",
            created_by=reverted_by,
        )
        db.add(new_version)
        
        # Update the partial's html_content
        partial.html_content = version.html_content
        partial.updated_by = reverted_by
        
        await db.flush()
        await db.refresh(new_version)
        
        logger.info(f"Reverted partial {partial_id} from v{version_number} to v{new_version.version_number}")
        
        return {
            "partial_id": str(partial_id),
            "reverted_from": version_number,
            "new_version": new_version.version_number,
            "message": f"Successfully reverted to version {version_number}",
        }


class LayoutPartialDefaultService:
    """Service for layout partial default rule operations."""
    
    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        partial_id: Optional[UUID] = None,
        scope: Optional[str] = None,
    ) -> tuple[List[LayoutPartialDefault], int]:
        """
        List default rules with filtering.
        
        Args:
            db: Database session
            partial_id: Filter by partial
            scope: Filter by scope
            
        Returns:
            Tuple of (defaults, total_count)
        """
        query = select(LayoutPartialDefault).options(
            selectinload(LayoutPartialDefault.partial),
            selectinload(LayoutPartialDefault.category)
        )
        count_query = select(func.count()).select_from(LayoutPartialDefault)
        
        if partial_id:
            query = query.where(LayoutPartialDefault.partial_id == str(partial_id))
            count_query = count_query.where(LayoutPartialDefault.partial_id == str(partial_id))
        
        if scope:
            query = query.where(LayoutPartialDefault.scope == scope)
            count_query = count_query.where(LayoutPartialDefault.scope == scope)
        
        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Execute main query
        query = query.order_by(LayoutPartialDefault.priority.desc())
        result = await db.execute(query)
        defaults = list(result.scalars().all())
        
        return defaults, total
    
    @staticmethod
    async def get_by_id(db: AsyncSession, default_id: UUID) -> Optional[LayoutPartialDefault]:
        """Get a default rule by ID."""
        result = await db.execute(
            select(LayoutPartialDefault)
            .options(
                selectinload(LayoutPartialDefault.partial),
                selectinload(LayoutPartialDefault.category)
            )
            .where(LayoutPartialDefault.id == str(default_id))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, data: LayoutPartialDefaultCreate) -> LayoutPartialDefault:
        """Create a new default rule."""
        default = LayoutPartialDefault(
            partial_id=str(data.partial_id),
            scope=data.scope,
            category_id=str(data.category_id) if data.category_id else None,
            medium=data.medium,
            priority=data.priority,
        )
        db.add(default)
        await db.flush()
        await db.refresh(default)
        
        logger.info(f"Created default rule for partial {data.partial_id}")
        return default
    
    @staticmethod
    async def update(
        db: AsyncSession,
        default_id: UUID,
        data: LayoutPartialDefaultUpdate
    ) -> Optional[LayoutPartialDefault]:
        """Update a default rule."""
        default = await LayoutPartialDefaultService.get_by_id(db, default_id)
        if not default:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Convert category_id to string if present
        if "category_id" in update_data and update_data["category_id"]:
            update_data["category_id"] = str(update_data["category_id"])
        
        for field, value in update_data.items():
            setattr(default, field, value)
        
        await db.flush()
        await db.refresh(default)
        
        logger.info(f"Updated default rule: {default.id}")
        return default
    
    @staticmethod
    async def delete(db: AsyncSession, default_id: UUID) -> bool:
        """Delete a default rule."""
        default = await LayoutPartialDefaultService.get_by_id(db, default_id)
        if not default:
            return False
        
        await db.delete(default)
        await db.flush()
        
        logger.info(f"Deleted default rule: {default_id}")
        return True
    
    @staticmethod
    async def get_default_for_context(
        db: AsyncSession,
        partial_type: str,  # 'header', 'footer', 'signature'
        *,
        category_id: Optional[UUID] = None,
        medium: Optional[str] = None,
    ) -> Optional[LayoutPartial]:
        """
        Get the default partial for a given context.
        
        Resolution order (highest to lowest priority):
        1. Category-specific default
        2. Medium-specific default
        3. Universal default (scope='all')
        
        Args:
            db: Database session
            partial_type: Type of partial to find
            category_id: Optional category context
            medium: Optional medium context (pdf, email, sms)
            
        Returns:
            The most appropriate default partial, or None
        """
        # Build query to find matching defaults
        query = (
            select(LayoutPartialDefault)
            .options(selectinload(LayoutPartialDefault.partial))
            .join(LayoutPartial)
            .where(LayoutPartial.type == partial_type)
        )
        
        # Try category-specific first
        if category_id:
            cat_result = await db.execute(
                query.where(LayoutPartialDefault.scope == "category")
                .where(LayoutPartialDefault.category_id == str(category_id))
                .order_by(LayoutPartialDefault.priority.desc())
                .limit(1)
            )
            default = cat_result.scalar_one_or_none()
            if default and default.partial:
                return default.partial
        
        # Try medium-specific
        if medium:
            med_result = await db.execute(
                query.where(LayoutPartialDefault.scope == "medium")
                .where(LayoutPartialDefault.medium == medium)
                .order_by(LayoutPartialDefault.priority.desc())
                .limit(1)
            )
            default = med_result.scalar_one_or_none()
            if default and default.partial:
                return default.partial
        
        # Fall back to universal
        all_result = await db.execute(
            query.where(LayoutPartialDefault.scope == "all")
            .order_by(LayoutPartialDefault.priority.desc())
            .limit(1)
        )
        default = all_result.scalar_one_or_none()
        if default and default.partial:
            return default.partial
        
        return None
