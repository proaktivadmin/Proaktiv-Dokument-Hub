"""
Office Service - Business logic for office management.
"""

import logging
import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import NO_VALUE

from app.config import settings
from app.models.employee import Employee
from app.models.office import Office
from app.models.office_territory import OfficeTerritory
from app.schemas.office import OfficeCreate, OfficeUpdate, OfficeWithStats
from app.services.notification_service import NotificationService
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)


class OfficeService:
    """Service for office CRUD operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        city: str | None = None,
        is_active: bool | None = None,
        office_type: str | None = None,
        include_sub: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Office], int]:
        """
        List offices with optional filtering.

        Args:
            db: Database session
            city: Filter by city
            is_active: Filter by active status
            office_type: Filter by office type ('main', 'sub', 'regional')
            include_sub: If False, exclude sub-offices from the list
            skip: Offset for pagination
            limit: Max results

        Returns:
            Tuple of (offices, total_count)
        """
        query = select(Office).options(
            selectinload(Office.employees),
            selectinload(Office.territories),
            selectinload(Office.sub_offices).selectinload(Office.employees),
        )
        count_query = select(func.count()).select_from(Office)

        # Apply filters
        if city:
            query = query.where(Office.city.ilike(f"%{city}%"))
            count_query = count_query.where(Office.city.ilike(f"%{city}%"))

        if is_active is not None:
            query = query.where(Office.is_active == is_active)
            count_query = count_query.where(Office.is_active == is_active)

        if office_type:
            query = query.where(Office.office_type == office_type)
            count_query = count_query.where(Office.office_type == office_type)
        elif not include_sub:
            # Exclude sub-offices (show only main and regional)
            query = query.where(Office.office_type != "sub")
            count_query = count_query.where(Office.office_type != "sub")

        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute main query with pagination
        query = query.order_by(Office.name).offset(skip).limit(limit)
        result = await db.execute(query)
        offices = list(result.scalars().all())

        return offices, total

    @staticmethod
    async def get_by_id(db: AsyncSession, office_id: UUID) -> Office | None:
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
                selectinload(Office.external_listings),
                selectinload(Office.sub_offices).selectinload(Office.employees),
            )
            .where(Office.id == str(office_id))
        )
        office = result.scalar_one_or_none()
        if office:
            sub_result = await db.execute(
                select(Office).options(selectinload(Office.employees)).where(Office.parent_office_id == office.id)
            )
            office.sub_offices = list(sub_result.scalars().all())
        return office

    @staticmethod
    async def get_by_short_code(db: AsyncSession, short_code: str) -> Office | None:
        """
        Get an office by short code.

        Args:
            db: Database session
            short_code: Office short code (e.g., 'STAV')

        Returns:
            Office or None
        """
        result = await db.execute(select(Office).where(Office.short_code == short_code.upper()))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_vitec_department_id(db: AsyncSession, department_id: int) -> Office | None:
        """
        Get an office by Vitec department ID.
        """
        result = await db.execute(select(Office).where(Office.vitec_department_id == department_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_organization_number(db: AsyncSession, org_number: str) -> Office | None:
        """
        Get an office by Norwegian organization number (organisasjonsnummer).
        This is the most reliable identifier for merging offices.
        """
        result = await db.execute(select(Office).where(Office.organization_number == org_number))
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
    async def update(db: AsyncSession, office_id: UUID, data: OfficeUpdate) -> Office | None:
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
    async def deactivate(db: AsyncSession, office_id: UUID) -> Office | None:
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
            select(func.count()).select_from(Employee).where(Employee.office_id == str(office_id))
        )
        employee_count = employee_count_query.scalar() or 0

        active_count_query = await db.execute(
            select(func.count())
            .select_from(Employee)
            .where(Employee.office_id == str(office_id))
            .where(Employee.status == "active")
        )
        active_count = active_count_query.scalar() or 0

        # Territory count
        territory_count_query = await db.execute(
            select(func.count())
            .select_from(OfficeTerritory)
            .where(OfficeTerritory.office_id == str(office_id))
            .where(not OfficeTerritory.is_blacklisted)
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
        from app.schemas.office import SubOfficeSummary

        state = sa_inspect(office)
        sub_loaded = state.attrs.sub_offices.loaded_value is not NO_VALUE

        employee_count = len(office.employees) if office.employees else 0
        active_count = len([e for e in (office.employees or []) if e.status == "active"])
        territory_count = len([t for t in (office.territories or []) if not t.is_blacklisted])

        # Build sub-offices list
        sub_offices_list = []
        if sub_loaded and office.sub_offices:
            for sub in office.sub_offices:
                sub_emp_count = len(sub.employees) if sub.employees else 0
                sub_offices_list.append(
                    SubOfficeSummary(
                        id=sub.id,
                        name=sub.name,
                        short_code=sub.short_code,
                        employee_count=sub_emp_count,
                        is_active=sub.is_active,
                    )
                )

        return OfficeWithStats(
            id=office.id,
            name=office.name,
            legal_name=office.legal_name,
            short_code=office.short_code,
            organization_number=office.organization_number,
            vitec_department_id=office.vitec_department_id,
            office_type=office.office_type,
            parent_office_id=office.parent_office_id,
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
            banner_image_url=office.banner_image_url,
            description=office.description,
            color=office.color,
            is_active=office.is_active,
            created_at=office.created_at,
            updated_at=office.updated_at,
            employee_count=employee_count,
            active_employee_count=active_count,
            territory_count=territory_count,
            sub_offices=sub_offices_list,
        )

    # =============================================================================
    # Vitec Hub Sync
    # =============================================================================

    @staticmethod
    def _normalize_text(value: str | None) -> str | None:
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
            result = await db.execute(select(Office).where(Office.short_code == candidate))
            if not result.scalar_one_or_none():
                return candidate
            suffix += 1
            trim_len = max(1, 10 - len(str(suffix)))
            candidate = f"{base[:trim_len]}{suffix}"

    @staticmethod
    def _map_department_payload(raw: dict) -> dict:
        # Marketing name is primary display name, legal name stored separately
        market_name = OfficeService._normalize_text(raw.get("marketName"))
        legal_name = OfficeService._normalize_text(raw.get("legalName"))
        fallback_name = raw.get("name") or "Vitec Office"

        # Use marketName first, then name, legal name as last resort
        display_name = market_name or OfficeService._normalize_text(raw.get("name")) or legal_name or fallback_name

        # Organization number for matching/merging (Norwegian: organisasjonsnummer)
        # Note: Vitec Hub uses British spelling "organisationNumber"
        org_number = OfficeService._normalize_text(
            raw.get("organisationNumber")  # Vitec Hub (British spelling)
            or raw.get("organizationNumber")  # American spelling fallback
            or raw.get("orgNumber")
            or raw.get("orgnr")
        )

        # Image URLs
        banner_url = OfficeService._normalize_text(
            raw.get("departmentImageUrl") or raw.get("imageUrl") or raw.get("bannerUrl")
        )
        profile_url = OfficeService._normalize_text(raw.get("logoUrl") or raw.get("profileImageUrl"))

        return {
            "vitec_department_id": raw.get("departmentId"),
            "department_number": raw.get("departmentNumber"),
            "name": display_name,
            "legal_name": legal_name,
            "organization_number": org_number,
            "email": OfficeService._normalize_text(raw.get("email")),
            "phone": OfficeService._normalize_text(raw.get("phone")),
            "street_address": OfficeService._normalize_text(raw.get("streetAddress") or raw.get("postalAddress")),
            "postal_code": OfficeService._normalize_text(raw.get("postalCode") or raw.get("visitPostalCode")),
            "city": OfficeService._normalize_text(raw.get("city") or raw.get("visitCity")),
            "description": OfficeService._normalize_text(raw.get("aboutDepartment")),
            "banner_image_url": banner_url,
            "profile_image_url": profile_url,
            "is_active": raw.get("webPublish"),
        }

    @staticmethod
    async def upsert_from_hub(db: AsyncSession, payload: dict) -> tuple[Office, str]:
        """
        Upsert an office from Vitec Hub data.

        Match priority:
        1. organization_number (most reliable for merging)
        2. vitec_department_id
        3. name (fallback)
        """
        existing = None
        org_number = payload.get("organization_number")
        department_id = payload.get("vitec_department_id")

        # Priority 1: Match by organization number (Norwegian: organisasjonsnummer)
        if org_number:
            existing = await OfficeService.get_by_organization_number(db, org_number)

        # Priority 2: Match by Vitec department ID
        if not existing and department_id is not None:
            existing = await OfficeService.get_by_vitec_department_id(db, department_id)

        # Priority 3: Match by name (fallback)
        if not existing and payload.get("name"):
            result = await db.execute(select(Office).where(Office.name == payload["name"]))
            existing = result.scalar_one_or_none()

        if not existing:
            base_code = str(payload.get("department_number") or payload.get("name") or "OFF")
            short_code = await OfficeService._ensure_unique_short_code(db, base_code)
            office = Office(
                name=payload.get("name") or "Vitec Office",
                legal_name=payload.get("legal_name"),
                short_code=short_code,
                organization_number=org_number,
                vitec_department_id=department_id,
                email=payload.get("email"),
                phone=payload.get("phone"),
                street_address=payload.get("street_address"),
                postal_code=payload.get("postal_code"),
                city=payload.get("city"),
                description=payload.get("description"),
                profile_image_url=payload.get("profile_image_url"),
                banner_image_url=payload.get("banner_image_url"),
                is_active=payload.get("is_active") if payload.get("is_active") is not None else True,
            )
            db.add(office)
            await db.flush()
            await db.refresh(office)
            try:
                await NotificationService.notify_office_added(db, office)
            except Exception as exc:
                logger.warning("Failed to create office added notification: %s", exc)
            return office, "created"

        updated = False
        changed_fields: list[str] = []

        # Update organization_number if we now have it
        if org_number and existing.organization_number != org_number:
            existing.organization_number = org_number
            updated = True
            changed_fields.append("organization_number")

        # Update department_id if we now have it
        if department_id is not None and existing.vitec_department_id != department_id:
            existing.vitec_department_id = department_id
            updated = True
            changed_fields.append("vitec_department_id")

        # Update other fields
        for field in [
            "name",
            "legal_name",
            "email",
            "phone",
            "street_address",
            "postal_code",
            "city",
            "description",
            "profile_image_url",
            "banner_image_url",
        ]:
            value = payload.get(field)
            if value is None:
                continue
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                updated = True
                changed_fields.append(field)

        if payload.get("is_active") is not None and existing.is_active != payload.get("is_active"):
            existing.is_active = payload.get("is_active")
            updated = True
            changed_fields.append("is_active")

        if updated:
            await db.flush()
            await db.refresh(existing)
            if changed_fields:
                try:
                    await NotificationService.notify_office_updated(db, existing, changed_fields)
                except Exception as exc:
                    logger.warning("Failed to create office updated notification: %s", exc)
            return existing, "updated"

        return existing, "skipped"

    @staticmethod
    async def sync_from_hub(
        db: AsyncSession,
        *,
        installation_id: str | None = None,
    ) -> dict:
        hub = VitecHubService()
        install_id = installation_id or settings.VITEC_INSTALLATION_ID
        if not install_id:
            raise HTTPException(status_code=500, detail="VITEC_INSTALLATION_ID is not configured.")

        departments = await hub.get_departments(install_id)
        created = updated = skipped = 0
        sync_errors: list[str] = []
        for raw in departments:
            payload = OfficeService._map_department_payload(raw or {})
            if not payload.get("name"):
                skipped += 1
                sync_errors.append("missing_office_name")
                continue
            _, action = await OfficeService.upsert_from_hub(db, payload)
            if action == "created":
                created += 1
            elif action == "updated":
                updated += 1
            else:
                skipped += 1

        # Explicitly commit all changes
        if sync_errors:
            try:
                await NotificationService.notify_sync_error(
                    db,
                    operation="office_sync",
                    error=f"{len(sync_errors)} offices failed to sync",
                )
            except Exception as exc:
                logger.warning("Failed to create office sync error notification: %s", exc)
        await db.commit()

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
