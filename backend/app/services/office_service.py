"""
Office Service - Business logic for office management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
import logging
import re

from fastapi import HTTPException

from app.models.office import Office
from app.models.employee import Employee
from app.models.office_territory import OfficeTerritory
from app.schemas.office import OfficeCreate, OfficeUpdate, OfficeWithStats
from app.config import settings
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)


class OfficeService:
    """Service for office CRUD operations."""
    
    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        city: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Office], int]:
        """
        List offices with optional filtering.
        
        Args:
            db: Database session
            city: Filter by city
            is_active: Filter by active status
            skip: Offset for pagination
            limit: Max results
            
        Returns:
            Tuple of (offices, total_count)
        """
        query = select(Office).options(
            selectinload(Office.employees),
            selectinload(Office.territories)
        )
        count_query = select(func.count()).select_from(Office)
        
        # Apply filters
        if city:
            query = query.where(Office.city.ilike(f"%{city}%"))
            count_query = count_query.where(Office.city.ilike(f"%{city}%"))
        
        if is_active is not None:
            query = query.where(Office.is_active == is_active)
            count_query = count_query.where(Office.is_active == is_active)
        
        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Execute main query with pagination
        query = query.order_by(Office.name).offset(skip).limit(limit)
        result = await db.execute(query)
        offices = list(result.scalars().all())
        
        return offices, total
    
    @staticmethod
    async def get_by_id(db: AsyncSession, office_id: UUID) -> Optional[Office]:
        """
        Get an office by ID with related entities.
        
        Args:
            db: Database session
            office_id: Office UUID
            
        Returns:
            Office or None
        """
        result = await db.execute(
            select(Office)
            .options(
                selectinload(Office.employees),
                selectinload(Office.territories),
                selectinload(Office.assets),
                selectinload(Office.external_listings)
            )
            .where(Office.id == str(office_id))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_short_code(db: AsyncSession, short_code: str) -> Optional[Office]:
        """
        Get an office by short code.
        
        Args:
            db: Database session
            short_code: Office short code (e.g., 'STAV')
            
        Returns:
            Office or None
        """
        result = await db.execute(
            select(Office).where(Office.short_code == short_code.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_vitec_department_id(
        db: AsyncSession,
        department_id: int
    ) -> Optional[Office]:
        """
        Get an office by Vitec department ID.
        """
        result = await db.execute(
            select(Office).where(Office.vitec_department_id == department_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, data: OfficeCreate) -> Office:
        """
        Create a new office.
        
        Args:
            db: Database session
            data: Office creation data
            
        Returns:
            Created office
        """
        office = Office(
            name=data.name,
            short_code=data.short_code.upper(),
            vitec_department_id=data.vitec_department_id,
            email=data.email,
            phone=data.phone,
            street_address=data.street_address,
            postal_code=data.postal_code,
            city=data.city,
            homepage_url=data.homepage_url,
            google_my_business_url=data.google_my_business_url,
            facebook_url=data.facebook_url,
            instagram_url=data.instagram_url,
            linkedin_url=data.linkedin_url,
            profile_image_url=data.profile_image_url,
            description=data.description,
            color=data.color,
            is_active=data.is_active,
        )
        db.add(office)
        await db.flush()
        await db.refresh(office)
        
        logger.info(f"Created office: {office.name} ({office.short_code})")
        return office
    
    @staticmethod
    async def update(
        db: AsyncSession,
        office_id: UUID,
        data: OfficeUpdate
    ) -> Optional[Office]:
        """
        Update an existing office.
        
        Args:
            db: Database session
            office_id: Office UUID
            data: Update data
            
        Returns:
            Updated office or None if not found
        """
        office = await OfficeService.get_by_id(db, office_id)
        if not office:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Uppercase short_code if provided
        if "short_code" in update_data:
            update_data["short_code"] = update_data["short_code"].upper()
        
        for field, value in update_data.items():
            setattr(office, field, value)
        
        await db.flush()
        await db.refresh(office)
        
        logger.info(f"Updated office: {office.name} ({office.id})")
        return office
    
    @staticmethod
    async def deactivate(db: AsyncSession, office_id: UUID) -> Optional[Office]:
        """
        Deactivate an office (soft delete).
        
        Args:
            db: Database session
            office_id: Office UUID
            
        Returns:
            Deactivated office or None if not found
        """
        office = await OfficeService.get_by_id(db, office_id)
        if not office:
            return None
        
        office.is_active = False
        await db.flush()
        await db.refresh(office)
        
        logger.info(f"Deactivated office: {office.name} ({office.id})")
        return office
    
    @staticmethod
    async def get_stats(db: AsyncSession, office_id: UUID) -> dict:
        """
        Get statistics for an office.
        
        Args:
            db: Database session
            office_id: Office UUID
            
        Returns:
            Dict with employee_count, active_employee_count, territory_count
        """
        # Employee counts
        employee_count_query = await db.execute(
            select(func.count()).select_from(Employee)
            .where(Employee.office_id == str(office_id))
        )
        employee_count = employee_count_query.scalar() or 0
        
        active_count_query = await db.execute(
            select(func.count()).select_from(Employee)
            .where(Employee.office_id == str(office_id))
            .where(Employee.status == "active")
        )
        active_count = active_count_query.scalar() or 0
        
        # Territory count
        territory_count_query = await db.execute(
            select(func.count()).select_from(OfficeTerritory)
            .where(OfficeTerritory.office_id == str(office_id))
            .where(OfficeTerritory.is_blacklisted == False)
        )
        territory_count = territory_count_query.scalar() or 0
        
        return {
            "employee_count": employee_count,
            "active_employee_count": active_count,
            "territory_count": territory_count,
        }
    
    @staticmethod
    def to_response_with_stats(office: Office) -> OfficeWithStats:
        """
        Convert an Office model to OfficeWithStats response.
        
        Args:
            office: Office model with loaded relationships
            
        Returns:
            OfficeWithStats schema
        """
        employee_count = len(office.employees) if office.employees else 0
        active_count = len([e for e in (office.employees or []) if e.status == "active"])
        territory_count = len([t for t in (office.territories or []) if not t.is_blacklisted])
        
        return OfficeWithStats(
            id=office.id,
            name=office.name,
            short_code=office.short_code,
            vitec_department_id=office.vitec_department_id,
            email=office.email,
            phone=office.phone,
            street_address=office.street_address,
            postal_code=office.postal_code,
            city=office.city,
            homepage_url=office.homepage_url,
            google_my_business_url=office.google_my_business_url,
            facebook_url=office.facebook_url,
            instagram_url=office.instagram_url,
            linkedin_url=office.linkedin_url,
            profile_image_url=office.profile_image_url,
            description=office.description,
            color=office.color,
            is_active=office.is_active,
            created_at=office.created_at,
            updated_at=office.updated_at,
            employee_count=employee_count,
            active_employee_count=active_count,
            territory_count=territory_count,
        )

    # =============================================================================
    # Vitec Hub Sync
    # =============================================================================

    @staticmethod
    def _normalize_text(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned if cleaned else None

    @staticmethod
    async def _ensure_unique_short_code(db: AsyncSession, base_code: str) -> str:
        base = re.sub(r"[^A-Z0-9]", "", (base_code or "").upper()) or "OFF"
        candidate = base[:10]
        suffix = 1
        while True:
            result = await db.execute(
                select(Office).where(Office.short_code == candidate)
            )
            if not result.scalar_one_or_none():
                return candidate
            suffix += 1
            trim_len = max(1, 10 - len(str(suffix)))
            candidate = f"{base[:trim_len]}{suffix}"

    @staticmethod
    def _map_department_payload(raw: dict) -> dict:
        name = raw.get("marketName") or raw.get("name") or raw.get("legalName") or "Vitec Office"
        return {
            "vitec_department_id": raw.get("departmentId"),
            "department_number": raw.get("departmentNumber"),
            "name": OfficeService._normalize_text(name),
            "email": OfficeService._normalize_text(raw.get("email")),
            "phone": OfficeService._normalize_text(raw.get("phone")),
            "street_address": OfficeService._normalize_text(raw.get("streetAddress") or raw.get("postalAddress")),
            "postal_code": OfficeService._normalize_text(raw.get("postalCode") or raw.get("visitPostalCode")),
            "city": OfficeService._normalize_text(raw.get("city") or raw.get("visitCity")),
            "description": OfficeService._normalize_text(raw.get("aboutDepartment")),
            "is_active": raw.get("webPublish"),
        }

    @staticmethod
    async def upsert_from_hub(db: AsyncSession, payload: dict) -> tuple[Office, str]:
        existing = None
        department_id = payload.get("vitec_department_id")
        if department_id is not None:
            existing = await OfficeService.get_by_vitec_department_id(db, department_id)
        if not existing and payload.get("name"):
            result = await db.execute(select(Office).where(Office.name == payload["name"]))
            existing = result.scalar_one_or_none()

        if not existing:
            base_code = str(payload.get("department_number") or payload.get("name") or "OFF")
            short_code = await OfficeService._ensure_unique_short_code(db, base_code)
            office = Office(
                name=payload.get("name") or "Vitec Office",
                short_code=short_code,
                vitec_department_id=department_id,
                email=payload.get("email"),
                phone=payload.get("phone"),
                street_address=payload.get("street_address"),
                postal_code=payload.get("postal_code"),
                city=payload.get("city"),
                description=payload.get("description"),
                is_active=payload.get("is_active") if payload.get("is_active") is not None else True,
            )
            db.add(office)
            await db.flush()
            await db.refresh(office)
            return office, "created"

        updated = False
        if department_id is not None and existing.vitec_department_id != department_id:
            existing.vitec_department_id = department_id
            updated = True

        for field in [
            "name",
            "email",
            "phone",
            "street_address",
            "postal_code",
            "city",
            "description",
        ]:
            value = payload.get(field)
            if value is None:
                continue
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                updated = True

        if payload.get("is_active") is not None and existing.is_active != payload.get("is_active"):
            existing.is_active = payload.get("is_active")
            updated = True

        if updated:
            await db.flush()
            await db.refresh(existing)
            return existing, "updated"

        return existing, "skipped"

    @staticmethod
    async def sync_from_hub(
        db: AsyncSession,
        *,
        installation_id: Optional[str] = None,
    ) -> dict:
        hub = VitecHubService()
        install_id = installation_id or settings.VITEC_INSTALLATION_ID
        if not install_id:
            raise HTTPException(status_code=500, detail="VITEC_INSTALLATION_ID is not configured.")

        departments = await hub.get_departments(install_id)
        created = updated = skipped = 0
        for raw in departments:
            payload = OfficeService._map_department_payload(raw or {})
            if not payload.get("name"):
                skipped += 1
                continue
            _, action = await OfficeService.upsert_from_hub(db, payload)
            if action == "created":
                created += 1
            elif action == "updated":
                updated += 1
            else:
                skipped += 1

        total = len(departments)
        logger.info(
            "Vitec Hub offices sync complete: total=%s created=%s updated=%s skipped=%s",
            total,
            created,
            updated,
            skipped,
        )
        return {
            "total": total,
            "synced": created + updated,
            "created": created,
            "updated": updated,
            "skipped": skipped,
        }
