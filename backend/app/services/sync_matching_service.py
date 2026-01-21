"""
Sync matching service for Vitec preview workflow.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from difflib import SequenceMatcher
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.office import Office
from app.schemas.sync import FieldDiff, RecordDiff
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService

logger = logging.getLogger(__name__)


class SyncMatchingService:
    OFFICE_FIELDS: Sequence[str] = (
        "name",
        "legal_name",
        "organization_number",
        "email",
        "phone",
        "street_address",
        "postal_code",
        "city",
    )
    EMPLOYEE_FIELDS: Sequence[str] = (
        "first_name",
        "last_name",
        "title",
        "email",
        "phone",
        "system_roles",
    )
    FUZZY_MATCH_THRESHOLD = 0.85

    @staticmethod
    def _normalize_comparison_value(value: Any) -> Any:
        if isinstance(value, list):
            return sorted(value)
        return value

    @staticmethod
    def _should_include_vitec_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, list) and not value:
            return False
        return True

    @staticmethod
    def _normalize_name(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().lower()
        return cleaned or None

    @staticmethod
    def generate_field_diffs(
        local_record: object | None,
        payload: dict,
        fields: Sequence[str],
    ) -> list[FieldDiff]:
        diffs: list[FieldDiff] = []
        for field_name in fields:
            vitec_value = payload.get(field_name)
            if not SyncMatchingService._should_include_vitec_value(vitec_value):
                continue
            local_value = getattr(local_record, field_name, None) if local_record else None
            comparable_local = SyncMatchingService._normalize_comparison_value(local_value)
            comparable_vitec = SyncMatchingService._normalize_comparison_value(vitec_value)

            if comparable_local == comparable_vitec:
                continue

            has_conflict = (
                comparable_local is not None and comparable_vitec is not None and comparable_local != comparable_vitec
            )
            diffs.append(
                FieldDiff(
                    field_name=field_name,
                    local_value=local_value,
                    vitec_value=vitec_value,
                    has_conflict=has_conflict,
                )
            )
        return diffs

    @staticmethod
    async def match_office(db: AsyncSession, raw_department: dict) -> RecordDiff:
        payload = OfficeService._map_department_payload(raw_department or {})
        match: Office | None = None
        match_method: str | None = None
        match_confidence = 0.0

        org_number = payload.get("organization_number")
        if org_number:
            match = await OfficeService.get_by_organization_number(db, org_number)
            if match:
                match_method = "organization_number"
                match_confidence = 1.0

        if not match and payload.get("vitec_department_id") is not None:
            match = await OfficeService.get_by_vitec_department_id(
                db,
                payload["vitec_department_id"],
            )
            if match:
                match_method = "vitec_department_id"
                match_confidence = 1.0

        normalized_name = SyncMatchingService._normalize_name(payload.get("name"))
        if not match and normalized_name:
            result = await db.execute(select(Office).where(func.lower(Office.name) == normalized_name))
            match = result.scalar_one_or_none()
            if match:
                match_method = "name_exact"
                match_confidence = 0.9

        if not match and normalized_name:
            result = await db.execute(select(Office))
            offices = result.scalars().all()
            best_match: Office | None = None
            best_ratio = 0.0
            for office in offices:
                office_name = SyncMatchingService._normalize_name(office.name) or ""
                ratio = SequenceMatcher(None, normalized_name, office_name).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = office
            if best_match and best_ratio >= SyncMatchingService.FUZZY_MATCH_THRESHOLD:
                match = best_match
                match_method = "name_fuzzy"
                match_confidence = 0.7

        display_name = payload.get("name") or (match.name if match else "Ukjent kontor")
        fields = SyncMatchingService.generate_field_diffs(
            match,
            payload,
            SyncMatchingService.OFFICE_FIELDS,
        )
        match_type = "matched" if match else "new"
        vitec_id = payload.get("vitec_department_id")
        vitec_id_str = str(vitec_id) if vitec_id is not None else None

        return RecordDiff(
            match_type=match_type,
            local_id=match.id if match else None,
            vitec_id=vitec_id_str,
            display_name=display_name,
            fields=fields,
            match_confidence=match_confidence,
            match_method=match_method,
        )

    @staticmethod
    async def match_employee(db: AsyncSession, raw_employee: dict) -> RecordDiff:
        payload = EmployeeService._map_employee_payload(raw_employee or {})
        match: Employee | None = None
        match_method: str | None = None
        match_confidence = 0.0

        vitec_employee_id = payload.get("vitec_employee_id")
        if vitec_employee_id:
            match = await EmployeeService.get_by_vitec_employee_id(db, vitec_employee_id)
            if match:
                match_method = "vitec_employee_id"
                match_confidence = 1.0

        email = payload.get("email")
        if not match and email:
            result = await db.execute(select(Employee).where(func.lower(Employee.email) == email.lower()))
            match = result.scalar_one_or_none()
            if match:
                match_method = "email"
                match_confidence = 0.95

        first_name = payload.get("first_name")
        last_name = payload.get("last_name")
        department_id = payload.get("department_id")
        if not match and first_name and last_name and department_id is not None:
            office = await OfficeService.get_by_vitec_department_id(db, department_id)
            if office:
                result = await db.execute(
                    select(Employee)
                    .where(Employee.first_name == first_name)
                    .where(Employee.last_name == last_name)
                    .where(Employee.office_id == str(office.id))
                )
                match = result.scalar_one_or_none()
                if match:
                    match_method = "name_office"
                    match_confidence = 0.8

        display_name_parts = [part for part in [first_name, last_name] if part]
        display_name = " ".join(display_name_parts)
        if not display_name and match:
            display_name = match.full_name
        if not display_name:
            display_name = "Ukjent ansatt"

        fields = SyncMatchingService.generate_field_diffs(
            match,
            payload,
            SyncMatchingService.EMPLOYEE_FIELDS,
        )
        match_type = "matched" if match else "new"
        vitec_id_str = str(vitec_employee_id) if vitec_employee_id is not None else None

        return RecordDiff(
            match_type=match_type,
            local_id=match.id if match else None,
            vitec_id=vitec_id_str,
            display_name=display_name,
            fields=fields,
            match_confidence=match_confidence,
            match_method=match_method,
        )
