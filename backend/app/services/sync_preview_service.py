"""
Sync preview service for Vitec review workflow.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.employee import Employee
from app.models.office import Office
from app.models.sync_session import SyncSession
from app.schemas.sync import RecordDiff, SyncPreview, SyncSummary
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService
from app.services.sync_matching_service import SyncMatchingService
from app.services.vitec_hub_service import VitecHubService


class SyncPreviewService:
    """Generate and store preview sessions for Vitec sync review."""

    def __init__(self) -> None:
        self._hub = VitecHubService()
        self._matching = SyncMatchingService()

    async def generate_preview(self, db: AsyncSession) -> SyncPreview:
        installation_id = settings.VITEC_INSTALLATION_ID
        if not installation_id:
            raise HTTPException(
                status_code=500,
                detail="VITEC_INSTALLATION_ID is not configured.",
            )

        departments = await self._hub.get_departments(installation_id)
        employees = await self._hub.get_employees(installation_id)

        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=24)

        session = SyncSession(
            status="pending",
            preview_data={},
            decisions={},
            created_at=now,
            expires_at=expires_at,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)

        office_diffs, matched_offices, office_payloads = await self._build_office_diffs(db, departments)
        employee_diffs, matched_employees, missing_office, employee_payloads = await self._build_employee_diffs(
            db,
            employees,
        )

        office_not_in_vitec = await self._local_offices_not_in_vitec(db, matched_offices)
        employee_not_in_vitec = await self._local_employees_not_in_vitec(db, matched_employees)

        office_diffs.extend(office_not_in_vitec)
        employee_diffs.extend(employee_not_in_vitec)

        summary = SyncSummary(
            offices_new=sum(1 for diff in office_diffs if diff.match_type == "new"),
            offices_matched=sum(1 for diff in office_diffs if diff.match_type == "matched"),
            offices_not_in_vitec=sum(1 for diff in office_diffs if diff.match_type == "not_in_vitec"),
            employees_new=sum(1 for diff in employee_diffs if diff.match_type == "new"),
            employees_matched=sum(1 for diff in employee_diffs if diff.match_type == "matched"),
            employees_not_in_vitec=sum(1 for diff in employee_diffs if diff.match_type == "not_in_vitec"),
            employees_missing_office=missing_office,
        )

        preview = SyncPreview(
            session_id=session.id,
            created_at=now,
            expires_at=expires_at,
            offices=office_diffs,
            employees=employee_diffs,
            summary=summary,
        )

        preview_payload = preview.model_dump(mode="json")
        preview_payload["_payloads"] = {
            "offices": office_payloads,
            "employees": employee_payloads,
        }
        session.preview_data = preview_payload
        await db.flush()

        return preview

    async def get_session(self, db: AsyncSession, session_id: UUID) -> SyncPreview:
        session = await self._load_session(db, session_id)
        if session.expires_at < datetime.now(UTC):
            session.status = "expired"
            await db.flush()
            raise HTTPException(status_code=410, detail="Sync session has expired.")
        if not session.preview_data:
            raise HTTPException(status_code=404, detail="Sync preview not found.")
        preview_payload = dict(session.preview_data)
        preview_payload = self._apply_decisions(preview_payload, session.decisions or {})
        return SyncPreview.model_validate(preview_payload)

    async def cancel_session(self, db: AsyncSession, session_id: UUID) -> None:
        session = await self._load_session(db, session_id)
        session.status = "cancelled"
        await db.flush()

    async def _load_session(self, db: AsyncSession, session_id: UUID) -> SyncSession:
        result = await db.execute(select(SyncSession).where(SyncSession.id == str(session_id)))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Sync session not found.")
        return session

    def _apply_decisions(self, preview_payload: dict, decisions: dict) -> dict:
        if not decisions:
            return preview_payload

        for key, decision_key in [("offices", "office"), ("employees", "employee")]:
            record_decisions = decisions.get(decision_key, {})
            if not record_decisions:
                continue
            for record in preview_payload.get(key, []):
                record_id = str(record.get("local_id") or record.get("vitec_id") or "")
                if not record_id:
                    continue
                field_decisions = record_decisions.get(record_id, {})
                if not field_decisions:
                    continue
                for field in record.get("fields", []):
                    decision = field_decisions.get(field.get("field_name"))
                    if decision:
                        field["decision"] = decision
        return preview_payload

    async def _build_office_diffs(
        self,
        db: AsyncSession,
        departments: list[dict],
    ) -> tuple[list[RecordDiff], set[str], dict[str, dict]]:
        office_diffs: list[RecordDiff] = []
        matched_ids: set[str] = set()
        payloads: dict[str, dict] = {}

        for raw in departments:
            payload = OfficeService._map_department_payload(raw or {})
            vitec_id = payload.get("vitec_department_id")
            if vitec_id is not None:
                payloads[str(vitec_id)] = payload
            diff = await self._matching.match_office(db, raw or {})
            office_diffs.append(diff)
            if diff.match_type == "matched" and diff.local_id:
                matched_ids.add(str(diff.local_id))
        return office_diffs, matched_ids, payloads

    async def _build_employee_diffs(
        self,
        db: AsyncSession,
        employees: list[dict],
    ) -> tuple[list[RecordDiff], set[str], int, dict[str, dict]]:
        employee_diffs: list[RecordDiff] = []
        matched_ids: set[str] = set()
        missing_office = 0
        payloads: dict[str, dict] = {}

        office_lookup = await self._office_lookup(db)
        for raw in employees:
            payload = EmployeeService._map_employee_payload(raw or {})
            vitec_id = payload.get("vitec_employee_id")
            if vitec_id:
                payloads[str(vitec_id)] = payload
            department_id = payload.get("department_id")
            if department_id is None or department_id not in office_lookup:
                missing_office += 1

            diff = await self._matching.match_employee(db, raw or {})
            employee_diffs.append(diff)
            if diff.match_type == "matched" and diff.local_id:
                matched_ids.add(str(diff.local_id))
        return employee_diffs, matched_ids, missing_office, payloads

    async def _office_lookup(self, db: AsyncSession) -> dict[int, Office]:
        result = await db.execute(select(Office))
        offices = result.scalars().all()
        return {office.vitec_department_id: office for office in offices if office.vitec_department_id}

    async def _local_offices_not_in_vitec(
        self,
        db: AsyncSession,
        matched_ids: set[str],
    ) -> list[RecordDiff]:
        result = await db.execute(select(Office))
        offices = result.scalars().all()
        diffs: list[RecordDiff] = []
        for office in offices:
            if str(office.id) in matched_ids:
                continue
            diffs.append(
                RecordDiff(
                    match_type="not_in_vitec",
                    local_id=office.id,
                    vitec_id=None,
                    display_name=office.name,
                    fields=[],
                    match_confidence=0.0,
                    match_method=None,
                )
            )
        return diffs

    async def _local_employees_not_in_vitec(
        self,
        db: AsyncSession,
        matched_ids: set[str],
    ) -> list[RecordDiff]:
        result = await db.execute(select(Employee))
        employees = result.scalars().all()
        diffs: list[RecordDiff] = []
        for employee in employees:
            if str(employee.id) in matched_ids:
                continue
            diffs.append(
                RecordDiff(
                    match_type="not_in_vitec",
                    local_id=employee.id,
                    vitec_id=employee.vitec_employee_id,
                    display_name=employee.full_name,
                    fields=[],
                    match_confidence=0.0,
                    match_method=None,
                )
            )
        return diffs
