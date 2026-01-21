"""
Territory Service - Business logic for postal codes and office territories.
"""

import builtins
import logging
from uuid import UUID

import httpx
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.office_territory import OfficeTerritory
from app.models.postal_code import PostalCode
from app.schemas.territory import (
    OfficeTerritoryCreate,
    OfficeTerritoryUpdate,
    TerritoryFeature,
    TerritoryFeatureProperties,
    TerritoryMapData,
)

logger = logging.getLogger(__name__)


class PostalCodeService:
    """Service for postal code operations."""

    BRING_URL = "https://www.bring.no/postnummerregister-ansi.txt"

    @staticmethod
    async def list(db: AsyncSession) -> list[PostalCode]:
        """Get all postal codes."""
        result = await db.execute(select(PostalCode).order_by(PostalCode.postal_code))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_code(db: AsyncSession, postal_code: str) -> PostalCode | None:
        """Get a postal code by its code."""
        result = await db.execute(select(PostalCode).where(PostalCode.postal_code == postal_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def sync_from_bring(db: AsyncSession) -> dict:
        """
        Sync postal codes from Bring Postnummerregister.

        Returns:
            Dict with synced count and message
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(PostalCodeService.BRING_URL, timeout=30.0)
                response.raise_for_status()

                content = response.text
                lines = content.strip().split("\n")

                count = 0
                for line in lines:
                    # Format: POSTNR\tPOSTSTED\tKOMMUNENR\tKOMMUNE\tKATEGORI
                    parts = line.strip().split("\t")
                    if len(parts) >= 5:
                        postal_code = parts[0]
                        postal_name = parts[1]
                        municipality_code = parts[2]
                        municipality_name = parts[3]
                        category = parts[4]

                        # Upsert using PostgreSQL INSERT ... ON CONFLICT
                        stmt = (
                            pg_insert(PostalCode)
                            .values(
                                postal_code=postal_code,
                                postal_name=postal_name,
                                municipality_code=municipality_code,
                                municipality_name=municipality_name,
                                category=category,
                            )
                            .on_conflict_do_update(
                                index_elements=["postal_code"],
                                set_={
                                    "postal_name": postal_name,
                                    "municipality_code": municipality_code,
                                    "municipality_name": municipality_name,
                                    "category": category,
                                },
                            )
                        )
                        await db.execute(stmt)
                        count += 1

                await db.flush()

                logger.info(f"Synced {count} postal codes from Bring")
                return {"synced": count, "message": f"Successfully synced {count} postal codes"}

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch postal codes from Bring: {e}")
            return {"synced": 0, "message": f"Failed to fetch from Bring: {str(e)}"}
        except Exception as e:
            logger.error(f"Error syncing postal codes: {e}")
            return {"synced": 0, "message": f"Error: {str(e)}"}


class OfficeTerritoryService:
    """Service for office territory operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        office_id: UUID | None = None,
        source: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[OfficeTerritory], int]:
        """
        List territories with filtering.

        Args:
            db: Database session
            office_id: Filter by office
            source: Filter by source
            skip: Offset for pagination
            limit: Max results

        Returns:
            Tuple of (territories, total_count)
        """
        query = select(OfficeTerritory).options(
            selectinload(OfficeTerritory.office), selectinload(OfficeTerritory.postal_code_info)
        )
        count_query = select(func.count()).select_from(OfficeTerritory)

        if office_id:
            query = query.where(OfficeTerritory.office_id == str(office_id))
            count_query = count_query.where(OfficeTerritory.office_id == str(office_id))

        if source:
            query = query.where(OfficeTerritory.source == source)
            count_query = count_query.where(OfficeTerritory.source == source)

        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute main query
        query = query.order_by(OfficeTerritory.postal_code).offset(skip).limit(limit)
        result = await db.execute(query)
        territories = list(result.scalars().all())

        return territories, total

    @staticmethod
    async def get_by_id(db: AsyncSession, territory_id: UUID) -> OfficeTerritory | None:
        """Get a territory by ID."""
        result = await db.execute(
            select(OfficeTerritory)
            .options(selectinload(OfficeTerritory.office), selectinload(OfficeTerritory.postal_code_info))
            .where(OfficeTerritory.id == str(territory_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: OfficeTerritoryCreate) -> OfficeTerritory:
        """Create a new territory assignment."""
        territory = OfficeTerritory(
            office_id=str(data.office_id),
            postal_code=data.postal_code,
            source=data.source,
            priority=data.priority,
            is_blacklisted=data.is_blacklisted,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
        )
        db.add(territory)
        await db.flush()
        await db.refresh(territory)

        logger.info(f"Created territory: {data.postal_code} -> {data.office_id}")
        return territory

    @staticmethod
    async def update(db: AsyncSession, territory_id: UUID, data: OfficeTerritoryUpdate) -> OfficeTerritory | None:
        """Update a territory assignment."""
        territory = await OfficeTerritoryService.get_by_id(db, territory_id)
        if not territory:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(territory, field, value)

        await db.flush()
        await db.refresh(territory)

        logger.info(f"Updated territory: {territory.id}")
        return territory

    @staticmethod
    async def delete(db: AsyncSession, territory_id: UUID) -> bool:
        """Delete a territory assignment."""
        territory = await OfficeTerritoryService.get_by_id(db, territory_id)
        if not territory:
            return False

        await db.delete(territory)
        await db.flush()

        logger.info(f"Deleted territory: {territory_id}")
        return True

    @staticmethod
    async def get_blacklist(db: AsyncSession) -> builtins.list[str]:
        """Get all blacklisted postal codes."""
        result = await db.execute(select(OfficeTerritory.postal_code).where(OfficeTerritory.is_blacklisted).distinct())
        return [row[0] for row in result.all()]

    @staticmethod
    async def add_to_blacklist(db: AsyncSession, postal_code: str, office_id: UUID) -> OfficeTerritory:
        """Add a postal code to blacklist."""
        # Check if already exists
        existing = await db.execute(
            select(OfficeTerritory)
            .where(OfficeTerritory.office_id == str(office_id))
            .where(OfficeTerritory.postal_code == postal_code)
            .where(OfficeTerritory.source == "other")
        )
        territory = existing.scalar_one_or_none()

        if territory:
            territory.is_blacklisted = True
        else:
            territory = OfficeTerritory(
                office_id=str(office_id),
                postal_code=postal_code,
                source="other",
                is_blacklisted=True,
            )
            db.add(territory)

        await db.flush()
        await db.refresh(territory)

        logger.info(f"Blacklisted postal code: {postal_code}")
        return territory

    @staticmethod
    async def get_available_sources(db: AsyncSession) -> builtins.list[str]:
        """Get list of sources that have territories."""
        result = await db.execute(select(OfficeTerritory.source).distinct())
        return [row[0] for row in result.all()]

    @staticmethod
    async def get_map_data(db: AsyncSession, layers: builtins.list[str] | None = None) -> TerritoryMapData:
        """
        Get GeoJSON data for territory map.

        Note: This returns feature properties only. Actual geometry
        would need to be joined from a postal code geometry table
        or fetched from an external source.

        Args:
            db: Database session
            layers: List of source layers to include

        Returns:
            TerritoryMapData with features
        """
        query = select(OfficeTerritory).options(
            selectinload(OfficeTerritory.office), selectinload(OfficeTerritory.postal_code_info)
        )

        if layers:
            query = query.where(OfficeTerritory.source.in_(layers))

        result = await db.execute(query)
        territories = list(result.scalars().all())

        features = []
        for t in territories:
            feature = TerritoryFeature(
                type="Feature",
                properties=TerritoryFeatureProperties(
                    postal_code=t.postal_code,
                    postal_name=t.postal_code_info.postal_name if t.postal_code_info else "",
                    office_id=str(t.office.id) if t.office else None,
                    office_name=t.office.name if t.office else None,
                    office_color=t.office.color if t.office else None,
                    source=t.source,
                    is_blacklisted=t.is_blacklisted,
                ),
                geometry={"type": "Polygon", "coordinates": []},  # Placeholder
            )
            features.append(feature)

        return TerritoryMapData(features=features)

    @staticmethod
    async def import_from_csv(
        db: AsyncSession, data: builtins.list[dict], office_id: UUID, source: str = "vitec_next"
    ) -> dict:
        """
        Import territories from CSV data.

        Expected format: [{"postal_code": "0001", "priority": 1}, ...]

        Args:
            db: Database session
            data: List of territory data
            office_id: Office to assign territories to
            source: Source identifier

        Returns:
            Dict with imported count and errors
        """
        imported = 0
        errors = []

        for row in data:
            try:
                postal_code = row.get("postal_code")
                if not postal_code:
                    errors.append("Missing postal_code")
                    continue

                # Check if postal code exists
                pc = await PostalCodeService.get_by_code(db, postal_code)
                if not pc:
                    errors.append(f"Unknown postal code: {postal_code}")
                    continue

                # Upsert territory
                stmt = (
                    pg_insert(OfficeTerritory)
                    .values(
                        office_id=str(office_id),
                        postal_code=postal_code,
                        source=source,
                        priority=row.get("priority", 1),
                        is_blacklisted=row.get("is_blacklisted", False),
                    )
                    .on_conflict_do_update(
                        constraint="uq_office_territory_source",
                        set_={
                            "priority": row.get("priority", 1),
                            "is_blacklisted": row.get("is_blacklisted", False),
                        },
                    )
                )
                await db.execute(stmt)
                imported += 1

            except Exception as e:
                errors.append(f"Error importing {row}: {str(e)}")

        await db.flush()

        logger.info(f"Imported {imported} territories, {len(errors)} errors")
        return {"imported": imported, "errors": errors}
