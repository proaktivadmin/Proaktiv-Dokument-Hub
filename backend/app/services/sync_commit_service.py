"""
Sync commit service for Vitec review workflow.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_session import SyncSession
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.office import OfficeCreate, OfficeUpdate
from app.schemas.sync import SyncCommitResult, SyncDecisionUpdate
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService


class SyncCommitService:
    """Apply approved decisions from a sync session."""

    async def update_decision(
        self,
        db: AsyncSession,
        session_id: UUID,
        update: SyncDecisionUpdate,
    ) -> None:
        session = await self._load_session(db, session_id)
        if session.status != "pending":
            raise HTTPException(status_code=409, detail="Sync session is not editable.")

        decisions = session.decisions or {}
        record_map = decisions.setdefault(update.record_type, {})
        field_map = record_map.setdefault(update.record_id, {})
        field_map[update.field_name] = update.decision
        session.decisions = decisions
        await db.flush()

    async def commit_session(self, db: AsyncSession, session_id: UUID) -> SyncCommitResult:
        session = await self._load_session(db, session_id)
        if session.status == "committed":
            raise HTTPException(status_code=409, detail="Sync session already committed.")
        if session.status == "cancelled":
            raise HTTPException(status_code=409, detail="Sync session is cancelled.")

        if session.expires_at < datetime.now(UTC):
            session.status = "expired"
            await db.flush()
            raise HTTPException(status_code=410, detail="Sync session has expired.")

        preview_data = session.preview_data or {}
        decisions = session.decisions or {}
        payloads = preview_data.get("_payloads", {})
        office_payloads = payloads.get("offices", {})
        employee_payloads = payloads.get("employees", {})

        result = SyncCommitResult()
        await self._commit_offices(
            db,
            preview_data.get("offices", []),
            decisions.get("office", {}),
            office_payloads,
            result,
        )
        await self._commit_employees(
            db,
            preview_data.get("employees", []),
            decisions.get("employee", {}),
            employee_payloads,
            result,
        )

        session.status = "committed"
        await db.flush()

        return result

    async def _load_session(self, db: AsyncSession, session_id: UUID) -> SyncSession:
        result = await db.execute(select(SyncSession).where(SyncSession.id == str(session_id)))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Sync session not found.")
        return session

    async def _commit_offices(
        self,
        db: AsyncSession,
        office_records: list[dict[str, Any]],
        decisions: dict,
        payloads: dict,
        result: SyncCommitResult,
    ) -> None:
        for record in office_records:
            if record.get("match_type") == "not_in_vitec":
                continue

            record_id = str(record.get("local_id") or record.get("vitec_id") or "")
            accepted_fields = self._accepted_fields(
                record,
                decisions.get(record_id, {}),
            )

            if record.get("match_type") == "matched":
                local_id = record.get("local_id")
                if not local_id:
                    result.offices_skipped += 1
                    continue
                office = await OfficeService.get_by_id(db, local_id)
                if not office:
                    result.offices_skipped += 1
                    continue

                payload = payloads.get(str(record.get("vitec_id") or ""), {})
                if payload.get("vitec_department_id") and not office.vitec_department_id:
                    accepted_fields.setdefault("vitec_department_id", payload.get("vitec_department_id"))

                if not accepted_fields:
                    result.offices_skipped += 1
                    continue

                update = OfficeUpdate(**accepted_fields)
                updated = await OfficeService.update(db, local_id, update)
                if updated:
                    result.offices_updated += 1
                else:
                    result.offices_skipped += 1
                continue

            if record.get("match_type") == "new":
                if "name" not in accepted_fields:
                    result.offices_skipped += 1
                    continue

                payload = payloads.get(str(record.get("vitec_id") or ""), {})
                base_code = payload.get("department_number") or accepted_fields.get("name") or "OFF"
                short_code = await OfficeService._ensure_unique_short_code(db, str(base_code))

                create = OfficeCreate(
                    name=accepted_fields["name"],
                    short_code=short_code,
                    legal_name=accepted_fields.get("legal_name"),
                    organization_number=accepted_fields.get("organization_number"),
                    vitec_department_id=payload.get("vitec_department_id"),
                    email=accepted_fields.get("email"),
                    phone=accepted_fields.get("phone"),
                    street_address=accepted_fields.get("street_address"),
                    postal_code=accepted_fields.get("postal_code"),
                    city=accepted_fields.get("city"),
                )
                await OfficeService.create(db, create)
                result.offices_created += 1

    async def _commit_employees(
        self,
        db: AsyncSession,
        employee_records: list[dict[str, Any]],
        decisions: dict,
        payloads: dict,
        result: SyncCommitResult,
    ) -> None:
        for record in employee_records:
            if record.get("match_type") == "not_in_vitec":
                continue

            record_id = str(record.get("local_id") or record.get("vitec_id") or "")
            accepted_fields = self._accepted_fields(
                record,
                decisions.get(record_id, {}),
            )

            if record.get("match_type") == "matched":
                local_id = record.get("local_id")
                if not local_id:
                    result.employees_skipped += 1
                    continue
                employee = await EmployeeService.get_by_id(db, local_id)
                if not employee:
                    result.employees_skipped += 1
                    continue

                payload = payloads.get(str(record.get("vitec_id") or ""), {})
                if payload.get("vitec_employee_id") and not employee.vitec_employee_id:
                    accepted_fields.setdefault("vitec_employee_id", payload.get("vitec_employee_id"))

                if not accepted_fields:
                    result.employees_skipped += 1
                    continue

                update = EmployeeUpdate(**accepted_fields)
                updated = await EmployeeService.update(db, local_id, update)
                if updated:
                    result.employees_updated += 1
                else:
                    result.employees_skipped += 1
                continue

            if record.get("match_type") == "new":
                if "first_name" not in accepted_fields or "last_name" not in accepted_fields:
                    result.employees_skipped += 1
                    continue

                payload = payloads.get(str(record.get("vitec_id") or ""), {})
                department_id = payload.get("department_id")
                if department_id is None:
                    result.employees_skipped += 1
                    continue

                office = await OfficeService.get_by_vitec_department_id(db, department_id)
                if not office:
                    result.employees_skipped += 1
                    continue

                create = EmployeeCreate(
                    office_id=office.id,
                    vitec_employee_id=payload.get("vitec_employee_id"),
                    first_name=accepted_fields["first_name"],
                    last_name=accepted_fields["last_name"],
                    title=accepted_fields.get("title"),
                    email=accepted_fields.get("email"),
                    phone=accepted_fields.get("phone"),
                    system_roles=accepted_fields.get("system_roles") or [],
                )
                await EmployeeService.create(db, create)
                result.employees_created += 1

    def _accepted_fields(self, record: dict, decisions: dict) -> dict:
        accepted: dict[str, Any] = {}
        for field in record.get("fields", []):
            field_name = field.get("field_name")
            if decisions.get(field_name) == "accept":
                accepted[field_name] = field.get("vitec_value")
        return accepted
