"""
CompanyAsset Service - Business logic for company asset management.
"""

import builtins
import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company_asset import CompanyAsset
from app.schemas.company_asset import CompanyAssetUpdate

logger = logging.getLogger(__name__)


class CompanyAssetService:
    """Service for company asset CRUD operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        category: str | None = None,
        office_id: UUID | None = None,
        employee_id: UUID | None = None,
        is_global: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CompanyAsset], int]:
        """
        List assets with optional filtering.

        Args:
            db: Database session
            category: Filter by category
            office_id: Filter by office
            employee_id: Filter by employee
            is_global: Filter by global flag
            skip: Offset for pagination
            limit: Max results

        Returns:
            Tuple of (assets, total_count)
        """
        query = select(CompanyAsset).options(selectinload(CompanyAsset.office), selectinload(CompanyAsset.employee))
        count_query = select(func.count()).select_from(CompanyAsset)

        # Apply filters
        if category:
            query = query.where(CompanyAsset.category == category)
            count_query = count_query.where(CompanyAsset.category == category)

        if office_id:
            query = query.where(CompanyAsset.office_id == str(office_id))
            count_query = count_query.where(CompanyAsset.office_id == str(office_id))

        if employee_id:
            query = query.where(CompanyAsset.employee_id == str(employee_id))
            count_query = count_query.where(CompanyAsset.employee_id == str(employee_id))

        if is_global is not None:
            query = query.where(CompanyAsset.is_global == is_global)
            count_query = count_query.where(CompanyAsset.is_global == is_global)

        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute main query with pagination
        query = query.order_by(CompanyAsset.name).offset(skip).limit(limit)
        result = await db.execute(query)
        assets = list(result.scalars().all())

        return assets, total

    @staticmethod
    async def get_by_id(db: AsyncSession, asset_id: UUID) -> CompanyAsset | None:
        """
        Get an asset by ID with related entities.

        Args:
            db: Database session
            asset_id: Asset UUID

        Returns:
            CompanyAsset or None
        """
        result = await db.execute(
            select(CompanyAsset)
            .options(selectinload(CompanyAsset.office), selectinload(CompanyAsset.employee))
            .where(CompanyAsset.id == str(asset_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        filename: str,
        category: str,
        content_type: str,
        file_size: int,
        storage_path: str,
        office_id: UUID | None = None,
        employee_id: UUID | None = None,
        is_global: bool = False,
        metadata: dict | None = None,
    ) -> CompanyAsset:
        """
        Create a new asset.

        Args:
            db: Database session
            name: Display name
            filename: Original filename
            category: Asset category
            content_type: MIME type
            file_size: File size in bytes
            storage_path: Path in storage (WebDAV/blob)
            office_id: Office ID for office-scoped assets
            employee_id: Employee ID for employee-scoped assets
            is_global: Whether asset is company-wide
            metadata: Additional metadata

        Returns:
            Created asset
        """
        asset = CompanyAsset(
            name=name,
            filename=filename,
            category=category,
            content_type=content_type,
            file_size=file_size,
            storage_path=storage_path,
            office_id=str(office_id) if office_id else None,
            employee_id=str(employee_id) if employee_id else None,
            is_global=is_global,
            metadata_json=metadata or {},
        )
        db.add(asset)
        await db.flush()
        await db.refresh(asset)

        logger.info(f"Created asset: {asset.name} ({asset.id})")
        return asset

    @staticmethod
    async def update(db: AsyncSession, asset_id: UUID, data: CompanyAssetUpdate) -> CompanyAsset | None:
        """
        Update an existing asset's metadata.

        Args:
            db: Database session
            asset_id: Asset UUID
            data: Update data

        Returns:
            Updated asset or None if not found
        """
        asset = await CompanyAssetService.get_by_id(db, asset_id)
        if not asset:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle metadata specially - merge with existing
        if "metadata" in update_data and update_data["metadata"]:
            existing = asset.metadata_json or {}
            existing.update(update_data["metadata"])
            asset.metadata_json = existing
            del update_data["metadata"]

        for field, value in update_data.items():
            setattr(asset, field, value)

        await db.flush()
        await db.refresh(asset)

        logger.info(f"Updated asset: {asset.name} ({asset.id})")
        return asset

    @staticmethod
    async def delete(db: AsyncSession, asset_id: UUID) -> bool:
        """
        Delete an asset.

        Note: This deletes the database record. The file in storage
        should be cleaned up separately.

        Args:
            db: Database session
            asset_id: Asset UUID

        Returns:
            True if deleted, False if not found
        """
        asset = await CompanyAssetService.get_by_id(db, asset_id)
        if not asset:
            return False

        await db.delete(asset)
        await db.flush()

        logger.info(f"Deleted asset: {asset.name} ({asset_id})")
        return True

    @staticmethod
    async def get_by_office(
        db: AsyncSession, office_id: UUID, *, category: str | None = None
    ) -> builtins.list[CompanyAsset]:
        """
        Get all assets for an office.

        Args:
            db: Database session
            office_id: Office UUID
            category: Optional category filter

        Returns:
            List of assets
        """
        query = select(CompanyAsset).where(CompanyAsset.office_id == str(office_id))

        if category:
            query = query.where(CompanyAsset.category == category)

        query = query.order_by(CompanyAsset.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_employee(
        db: AsyncSession, employee_id: UUID, *, category: str | None = None
    ) -> builtins.list[CompanyAsset]:
        """
        Get all assets for an employee.

        Args:
            db: Database session
            employee_id: Employee UUID
            category: Optional category filter

        Returns:
            List of assets
        """
        query = select(CompanyAsset).where(CompanyAsset.employee_id == str(employee_id))

        if category:
            query = query.where(CompanyAsset.category == category)

        query = query.order_by(CompanyAsset.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_global_assets(db: AsyncSession, *, category: str | None = None) -> builtins.list[CompanyAsset]:
        """
        Get all global (company-wide) assets.

        Args:
            db: Database session
            category: Optional category filter

        Returns:
            List of global assets
        """
        query = select(CompanyAsset).where(CompanyAsset.is_global)

        if category:
            query = query.where(CompanyAsset.category == category)

        query = query.order_by(CompanyAsset.name)
        result = await db.execute(query)
        return list(result.scalars().all())
