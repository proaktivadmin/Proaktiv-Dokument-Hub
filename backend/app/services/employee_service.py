"""
Employee Service - Business logic for employee management.
"""

import builtins
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.employee import Employee
from app.models.office import Office
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, StartOffboarding
from app.services.notification_service import NotificationService
from app.services.office_service import OfficeService
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for employee CRUD and lifecycle operations."""

    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        office_id: UUID | None = None,
        status: list[str] | None = None,
        employee_type: list[str] | None = None,
        role: str | None = None,
        is_featured: bool | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Employee], int]:
        """
        List employees with optional filtering.

        Args:
            db: Database session
            office_id: Filter by office
            status: Filter by status(es)
            employee_type: Filter by employee type(s) - internal, external, system
            role: Filter by Vitec system role
            is_featured: Filter by featured broker flag
            search: Search by name or email
            skip: Offset for pagination
            limit: Max results

        Returns:
            Tuple of (employees, total_count)
        """
        query = select(Employee).options(selectinload(Employee.office))
        count_query = select(func.count()).select_from(Employee)

        # Apply filters
        if office_id:
            query = query.where(Employee.office_id == str(office_id))
            count_query = count_query.where(Employee.office_id == str(office_id))

        if status:
            query = query.where(Employee.status.in_(status))
            count_query = count_query.where(Employee.status.in_(status))

        # Employee type filter (internal, external, system)
        if employee_type:
            query = query.where(Employee.employee_type.in_(employee_type))
            count_query = count_query.where(Employee.employee_type.in_(employee_type))

        if is_featured is not None:
            query = query.where(Employee.is_featured_broker == is_featured)
            count_query = count_query.where(Employee.is_featured_broker == is_featured)

        # Role filter: check if role is in system_roles JSONB array
        if role:
            role_filter = Employee.system_roles.cast(JSONB).contains([role.lower()])
            query = query.where(role_filter)
            count_query = count_query.where(role_filter)

        # Search filter: name or email
        if search:
            search_term = f"%{search.lower()}%"
            search_filter = or_(
                func.lower(Employee.first_name).ilike(search_term),
                func.lower(Employee.last_name).ilike(search_term),
                func.lower(Employee.email).ilike(search_term),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute main query with pagination
        query = query.order_by(Employee.last_name, Employee.first_name).offset(skip).limit(limit)
        result = await db.execute(query)
        employees = list(result.scalars().all())

        return employees, total

    @staticmethod
    async def get_by_id(db: AsyncSession, employee_id: UUID) -> Employee | None:
        """
        Get an employee by ID with related entities.

        Args:
            db: Database session
            employee_id: Employee UUID

        Returns:
            Employee or None
        """
        result = await db.execute(
            select(Employee)
            .options(
                selectinload(Employee.office),
                selectinload(Employee.assets),
                selectinload(Employee.external_listings),
                selectinload(Employee.checklists),
            )
            .where(Employee.id == str(employee_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Employee | None:
        """
        Get an employee by email.

        Args:
            db: Database session
            email: Employee email

        Returns:
            Employee or None
        """
        result = await db.execute(
            select(Employee).options(selectinload(Employee.office)).where(Employee.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_vitec_employee_id(db: AsyncSession, vitec_employee_id: str) -> Employee | None:
        """
        Get an employee by Vitec employee ID.
        """
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.office))
            .where(Employee.vitec_employee_id == vitec_employee_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: EmployeeCreate) -> Employee:
        """
        Create a new employee.

        Args:
            db: Database session
            data: Employee creation data

        Returns:
            Created employee
        """
        employee = Employee(
            office_id=str(data.office_id),
            vitec_employee_id=data.vitec_employee_id,
            employee_type=data.employee_type,
            external_company=data.external_company,
            first_name=data.first_name,
            last_name=data.last_name,
            title=data.title,
            email=data.email,
            phone=data.phone,
            homepage_profile_url=data.homepage_profile_url,
            linkedin_url=data.linkedin_url,
            facebook_url=data.facebook_url,
            instagram_url=data.instagram_url,
            twitter_url=data.twitter_url,
            sharepoint_folder_url=data.sharepoint_folder_url,
            profile_image_url=data.profile_image_url,
            description=data.description,
            system_roles=data.system_roles,
            status=data.status,
            entra_upn=data.entra_upn,
            entra_upn_mismatch=data.entra_upn_mismatch,
            entra_user_id=data.entra_user_id,
            entra_mail=data.entra_mail,
            entra_display_name=data.entra_display_name,
            entra_given_name=data.entra_given_name,
            entra_surname=data.entra_surname,
            entra_job_title=data.entra_job_title,
            entra_mobile_phone=data.entra_mobile_phone,
            entra_department=data.entra_department,
            entra_office_location=data.entra_office_location,
            entra_street_address=data.entra_street_address,
            entra_postal_code=data.entra_postal_code,
            entra_country=data.entra_country,
            entra_account_enabled=data.entra_account_enabled,
            entra_mismatch_fields=data.entra_mismatch_fields,
            entra_last_synced_at=data.entra_last_synced_at,
            is_featured_broker=data.is_featured_broker,
            start_date=data.start_date,
            end_date=data.end_date,
            hide_from_homepage_date=data.hide_from_homepage_date,
            delete_data_date=data.delete_data_date,
        )
        db.add(employee)
        await db.flush()
        await db.refresh(employee)

        logger.info(f"Created employee: {employee.full_name} ({employee.id})")
        return employee

    @staticmethod
    async def update(db: AsyncSession, employee_id: UUID, data: EmployeeUpdate) -> Employee | None:
        """
        Update an existing employee.

        Args:
            db: Database session
            employee_id: Employee UUID
            data: Update data

        Returns:
            Updated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Convert office_id to string if present
        if "office_id" in update_data:
            update_data["office_id"] = str(update_data["office_id"])

        for field, value in update_data.items():
            setattr(employee, field, value)

        await db.flush()
        await db.refresh(employee)

        logger.info(f"Updated employee: {employee.full_name} ({employee.id})")
        return employee

    @staticmethod
    async def start_offboarding(db: AsyncSession, employee_id: UUID, data: StartOffboarding) -> Employee | None:
        """
        Start the offboarding process for an employee.

        Args:
            db: Database session
            employee_id: Employee UUID
            data: Offboarding data

        Returns:
            Updated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None

        employee.status = "offboarding"
        employee.end_date = data.end_date
        employee.hide_from_homepage_date = data.hide_from_homepage_date
        employee.delete_data_date = data.delete_data_date

        await db.flush()
        await db.refresh(employee)

        logger.info(f"Started offboarding for: {employee.full_name} ({employee.id})")
        return employee

    @staticmethod
    async def deactivate(db: AsyncSession, employee_id: UUID) -> Employee | None:
        """
        Deactivate an employee (mark as inactive).

        Args:
            db: Database session
            employee_id: Employee UUID

        Returns:
            Deactivated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None

        employee.status = "inactive"
        await db.flush()
        await db.refresh(employee)

        logger.info(f"Deactivated employee: {employee.full_name} ({employee.id})")
        return employee

    @staticmethod
    async def get_by_office(
        db: AsyncSession, office_id: UUID, *, status: builtins.list[str] | None = None
    ) -> builtins.list[Employee]:
        """
        Get all employees for an office.

        Args:
            db: Database session
            office_id: Office UUID
            status: Filter by status(es)

        Returns:
            List of employees
        """
        query = select(Employee).where(Employee.office_id == str(office_id))

        if status:
            query = query.where(Employee.status.in_(status))

        query = query.order_by(Employee.last_name, Employee.first_name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_offboarding_due(db: AsyncSession) -> builtins.list[Employee]:
        """
        Get employees with offboarding tasks due.

        Returns employees who are offboarding and have dates in the past.

        Args:
            db: Database session

        Returns:
            List of employees needing attention
        """
        from datetime import date

        today = date.today()

        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.office))
            .where(Employee.status == "offboarding")
            .where((Employee.hide_from_homepage_date <= today) | (Employee.delete_data_date <= today))
        )
        return list(result.scalars().all())

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
    def _split_name(full_name: str) -> tuple[str, str]:
        parts = (full_name or "").strip().split()
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])

    @staticmethod
    def _extract_department_id(value: object) -> int | None:
        if isinstance(value, list) and value:
            value = value[0]
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def _infer_roles_from_title(title: str | None) -> builtins.list[str]:
        if not title:
            return []
        mapping = {
            "eiendomsmeglerfullmektig": "eiendomsmeglerfullmektig",
            "eiendomsmegler": "eiendomsmegler",
            "fagansvarlig": "fagansvarlig",
            "daglig leder": "daglig_leder",
        }
        roles: list[str] = []
        lower = title.lower()
        for key, role in mapping.items():
            if key in lower and role not in roles:
                roles.append(role)
        return roles

    @staticmethod
    def _map_employee_roles(positions: builtins.list[dict] | None, title: str | None) -> builtins.list[str]:
        role_map = {
            1: "eiendomsmegler",
            2: "daglig_leder",
            3: "fagansvarlig",
            4: "antihvitvaskingsansvarlig",
            5: "medhjelper",
            6: "oppgjor",
            7: "administrasjon",
            8: "eiendomsmeglerfullmektig",
            9: "salgsleder",
            10: "kontorleder",
        }
        roles: list[str] = []
        for position in positions or []:
            if not isinstance(position, dict):
                continue
            pos_type = position.get("type")
            if isinstance(pos_type, dict):
                pos_type = pos_type.get("value") or pos_type.get("id")
            if isinstance(pos_type, int) and pos_type in role_map:
                role = role_map[pos_type]
                if role not in roles:
                    roles.append(role)
        if not roles:
            roles = EmployeeService._infer_roles_from_title(title)
        return roles

    @staticmethod
    def _map_employee_payload(raw: dict) -> dict:
        name = raw.get("name") or ""
        first_name, last_name = EmployeeService._split_name(name)
        title = EmployeeService._normalize_text(raw.get("title"))
        roles = EmployeeService._map_employee_roles(raw.get("employeePositions"), title)
        active_flag = raw.get("employeeActive")
        status = "active" if active_flag is True else "inactive" if active_flag is False else "active"

        # Profile image URL - try multiple possible field names
        profile_image_url = EmployeeService._normalize_text(
            raw.get("imageUrl")
            or raw.get("profileImageUrl")
            or raw.get("profileImage")
            or raw.get("photoUrl")
            or raw.get("avatarUrl")
        )

        return {
            "vitec_employee_id": raw.get("employeeId"),
            "department_id": EmployeeService._extract_department_id(raw.get("departmentId")),
            "first_name": EmployeeService._normalize_text(first_name),
            "last_name": EmployeeService._normalize_text(last_name),
            "title": title,
            "email": EmployeeService._normalize_text(raw.get("email")),
            "phone": EmployeeService._normalize_text(raw.get("mobilePhone") or raw.get("workPhone")),
            "description": EmployeeService._normalize_text(raw.get("aboutMe")),
            "profile_image_url": profile_image_url,
            "system_roles": roles,
            "status": status,
        }

    @staticmethod
    async def upsert_from_hub(db: AsyncSession, payload: dict, office: Office) -> tuple[Employee, str]:
        existing = None
        vitec_employee_id = payload.get("vitec_employee_id")
        if vitec_employee_id:
            existing = await EmployeeService.get_by_vitec_employee_id(db, vitec_employee_id)
        if not existing and payload.get("email"):
            existing = await EmployeeService.get_by_email(db, payload["email"])
        if not existing and payload.get("first_name") and payload.get("last_name"):
            result = await db.execute(
                select(Employee)
                .where(Employee.first_name == payload["first_name"])
                .where(Employee.last_name == payload["last_name"])
                .where(Employee.office_id == str(office.id))
            )
            existing = result.scalar_one_or_none()

        if not existing:
            employee = Employee(
                office_id=str(office.id),
                vitec_employee_id=vitec_employee_id,
                first_name=payload.get("first_name") or "",
                last_name=payload.get("last_name") or "",
                title=payload.get("title"),
                email=payload.get("email"),
                phone=payload.get("phone"),
                description=payload.get("description"),
                profile_image_url=payload.get("profile_image_url"),
                system_roles=payload.get("system_roles") or [],
                status=payload.get("status") or "active",
            )
            db.add(employee)
            await db.flush()
            await db.refresh(employee)
            try:
                await NotificationService.notify_employee_added(db, employee)
            except Exception as exc:
                logger.warning("Failed to create employee added notification: %s", exc)
            return employee, "created"

        updated = False
        changed_fields: list[str] = []
        if vitec_employee_id and existing.vitec_employee_id != vitec_employee_id:
            existing.vitec_employee_id = vitec_employee_id
            updated = True
            changed_fields.append("vitec_employee_id")
        if existing.office_id != str(office.id):
            existing.office_id = str(office.id)
            updated = True
            changed_fields.append("office_id")

        for field in [
            "first_name",
            "last_name",
            "title",
            "email",
            "phone",
            "description",
            "profile_image_url",
            "status",
        ]:
            value = payload.get(field)
            if value is None:
                continue
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                updated = True
                changed_fields.append(field)

        roles = payload.get("system_roles") or []
        if roles and existing.system_roles != roles:
            existing.system_roles = roles
            updated = True
            changed_fields.append("system_roles")

        if updated:
            await db.flush()
            await db.refresh(existing)
            if changed_fields:
                try:
                    await NotificationService.notify_employee_updated(db, existing, changed_fields)
                except Exception as exc:
                    logger.warning("Failed to create employee updated notification: %s", exc)
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

        employees = await hub.get_employees(install_id)
        created = updated = skipped = missing_office = 0
        sync_errors: list[str] = []

        for raw in employees:
            payload = EmployeeService._map_employee_payload(raw or {})
            if not payload.get("first_name") and not payload.get("last_name"):
                skipped += 1
                continue

            department_id = payload.get("department_id")
            if department_id is None:
                skipped += 1
                sync_errors.append("missing_department_id")
                continue

            office = await OfficeService.get_by_vitec_department_id(db, department_id)
            if not office:
                missing_office += 1
                sync_errors.append(f"missing_office:{department_id}")
                continue

            _, action = await EmployeeService.upsert_from_hub(db, payload, office)
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
                    operation="employee_sync",
                    error=f"{len(sync_errors)} employees failed to sync",
                )
            except Exception as exc:
                logger.warning("Failed to create employee sync error notification: %s", exc)
        await db.commit()

        total = len(employees)
        logger.info(
            "Vitec Hub employees sync complete: total=%s created=%s updated=%s skipped=%s missing_office=%s",
            total,
            created,
            updated,
            skipped,
            missing_office,
        )
        return {
            "total": total,
            "synced": created + updated,
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "missing_office": missing_office,
        }
