"""
Signature Service - Render personalized email signatures.
"""

from __future__ import annotations

import html as html_lib
import logging
import re
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee

logger = logging.getLogger(__name__)


class SignatureService:
    """Service for rendering email signatures."""

    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "scripts" / "templates"
    TEMPLATE_WITH_PHOTO = "email-signature.html"
    TEMPLATE_NO_PHOTO = "email-signature-no-photo.html"

    @staticmethod
    async def _get_employee_with_office(db: AsyncSession, employee_id: UUID) -> Employee | None:
        result = await db.execute(
            select(Employee).options(selectinload(Employee.office)).where(Employee.id == str(employee_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _resolve_template_path(version: str) -> Path:
        template_name = (
            SignatureService.TEMPLATE_NO_PHOTO if version == "no-photo" else SignatureService.TEMPLATE_WITH_PHOTO
        )
        return SignatureService.TEMPLATES_DIR / template_name

    @staticmethod
    def _render_template(template_content: str, employee: Employee) -> str:
        office = employee.office
        office_postal = ""
        if office and (office.postal_code or office.city):
            office_postal = f"{office.postal_code or ''} {office.city or ''}".strip()

        replacements = {
            "{{DisplayName}}": employee.full_name,
            "{{JobTitle}}": employee.title or "",
            "{{MobilePhone}}": employee.phone or "",
            "{{Email}}": employee.email or "",
            "{{OfficeName}}": office.name if office else "",
            "{{OfficeAddress}}": office.street_address if office else "",
            "{{OfficePostal}}": office_postal,
        }

        rendered = template_content
        for key, value in replacements.items():
            rendered = rendered.replace(key, value or "")

        return rendered

    @staticmethod
    def _strip_html(value: str) -> str:
        if not value:
            return ""
        text = re.sub(r"(?i)<br\s*/?>", "\n", value)
        text = re.sub(r"(?i)</(tr|p|div|table|li|ul|ol)>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = html_lib.unescape(text)
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    async def render_signature(db: AsyncSession, employee_id: UUID, version: str) -> dict | None:
        employee = await SignatureService._get_employee_with_office(db, employee_id)
        if not employee:
            return None

        template_path = SignatureService._resolve_template_path(version)
        try:
            template_content = template_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning("Signature template not found: %s", template_path)
            template_content = "<p>{{DisplayName}}<br>{{JobTitle}}<br>{{Email}}</p>"

        html_signature = SignatureService._render_template(template_content, employee)
        text_signature = SignatureService._strip_html(html_signature)

        return {
            "html": html_signature,
            "text": text_signature,
            "employee_name": employee.full_name,
            "employee_email": employee.email or "",
        }
