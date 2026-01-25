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

PLACEHOLDER_PHOTO = "https://proaktiv.no/assets/logos/lilje_clean_52.png"

# Company-wide social media defaults (used when office/employee doesn't have specific URLs)
DEFAULT_FACEBOOK = "https://www.facebook.com/proaktiveiendom"
DEFAULT_INSTAGRAM = "https://www.instagram.com/proaktiveiendomsmegling/"
DEFAULT_LINKEDIN = "https://no.linkedin.com/company/proaktiv-eiendomsmegling"


class SignatureService:
    """Service for rendering email signatures."""

    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "scripts" / "templates"
    TEMPLATE_WITH_PHOTO = "email-signature.html"
    TEMPLATE_NO_PHOTO = "email-signature-no-photo.html"

    @staticmethod
    def _format_phone_number(phone: str | None) -> str:
        """Format phone number as Norwegian style: XX XX XX XX.

        Handles various input formats:
        - 12345678 -> 12 34 56 78
        - +4712345678 -> +47 12 34 56 78
        - 004712345678 -> +47 12 34 56 78
        - Already formatted numbers are normalized
        """
        if not phone:
            return ""

        # Remove all non-digit characters except leading +
        has_plus = phone.startswith("+")
        digits = re.sub(r"\D", "", phone)

        if not digits:
            return phone  # Return original if no digits

        # Handle Norwegian country code
        if digits.startswith("47") and len(digits) >= 10:
            # +47 or 0047 prefix
            country_code = "+47"
            local_number = digits[2:]
        elif digits.startswith("0047") and len(digits) >= 12:
            country_code = "+47"
            local_number = digits[4:]
        elif has_plus and len(digits) >= 10:
            # Other country code with +
            country_code = f"+{digits[:2]}"
            local_number = digits[2:]
        else:
            # No country code, assume local Norwegian number
            country_code = ""
            local_number = digits

        # Format local number as double-digit groups (XX XX XX XX)
        # Norwegian mobile: 8 digits, landline: 8 digits
        formatted_local = " ".join(local_number[i : i + 2] for i in range(0, len(local_number), 2))

        if country_code:
            return f"{country_code} {formatted_local}"
        return formatted_local

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
    def _resolve_employee_photo_url(employee: Employee) -> str:
        photo_url = (employee.profile_image_url or "").strip()
        if photo_url and not photo_url.startswith("/api/vitec"):
            return photo_url
        return PLACEHOLDER_PHOTO

    @staticmethod
    def _resolve_social_urls(employee: Employee) -> dict[str, str]:
        """Resolve social media URLs with priority: employee > office > company default."""
        office = employee.office

        # Facebook: employee -> office -> default
        facebook = (
            getattr(employee, "facebook_url", None) or (office.facebook_url if office else None) or DEFAULT_FACEBOOK
        )

        # Instagram: employee -> office -> default
        instagram = (
            getattr(employee, "instagram_url", None) or (office.instagram_url if office else None) or DEFAULT_INSTAGRAM
        )

        # LinkedIn: employee -> office -> default
        linkedin = (
            getattr(employee, "linkedin_url", None) or (office.linkedin_url if office else None) or DEFAULT_LINKEDIN
        )

        return {
            "facebook_url": facebook,
            "instagram_url": instagram,
            "linkedin_url": linkedin,
        }

    @staticmethod
    def _render_template(template_content: str, employee: Employee) -> str:
        office = employee.office
        office_postal = ""
        if office and (office.postal_code or office.city):
            office_postal = f"{office.postal_code or ''} {office.city or ''}".strip()

        # Format phone number as Norwegian style (XX XX XX XX)
        formatted_phone = SignatureService._format_phone_number(employee.phone)
        # Raw phone for tel: links (digits only, with country code)
        raw_phone = re.sub(r"\D", "", employee.phone or "")
        if raw_phone and not raw_phone.startswith("47"):
            raw_phone = f"47{raw_phone}"  # Add Norwegian country code
        raw_phone = f"+{raw_phone}" if raw_phone else ""

        employee_photo_url = SignatureService._resolve_employee_photo_url(employee)
        social_urls = SignatureService._resolve_social_urls(employee)

        # Use employee's homepage URL if available, otherwise default to proaktiv.no
        employee_url = employee.homepage_url or "https://proaktiv.no/"

        replacements = {
            "{{DisplayName}}": employee.full_name,
            "{{JobTitle}}": employee.title or "",
            "{{MobilePhone}}": formatted_phone,
            "{{MobilePhoneRaw}}": raw_phone,
            "{{Email}}": employee.email or "",
            "{{EmployeePhotoUrl}}": employee_photo_url,
            "{{EmployeeUrl}}": employee_url,
            "{{FacebookUrl}}": social_urls["facebook_url"],
            "{{InstagramUrl}}": social_urls["instagram_url"],
            "{{LinkedInUrl}}": social_urls["linkedin_url"],
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
