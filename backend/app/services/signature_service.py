"""
Signature Service - Render personalized email signatures.
"""

from __future__ import annotations

import html as html_lib
import logging
import os
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
        """Return the signature photo URL as an absolute URL.

        Uses the server-side crop endpoint so the image is always
        exactly 80×96 — no client-side CSS tricks needed.
        Falls back to the placeholder logo when no photo is available.

        The URL must be absolute because the signature HTML is pasted
        into email clients which cannot resolve relative paths.
        """
        photo_url = (employee.profile_image_url or "").strip()
        if photo_url and not photo_url.startswith("/api/vitec"):
            base = os.getenv("FRONTEND_URL", "https://proaktiv-dokument-hub.vercel.app").strip().rstrip("/")
            return f"{base}/api/signatures/{employee.id}/photo"
        return PLACEHOLDER_PHOTO

    @staticmethod
    def _resolve_social_urls(employee: Employee) -> dict[str, str]:
        """Resolve social media URLs with priority: office > company default.

        Note: Employee-level social links are stored but not used in signatures yet.
        Future feature will allow employees to add personal links below the email line.
        """
        office = employee.office

        # Facebook: office -> default (strip to catch empty strings)
        facebook = ((office.facebook_url or "").strip() if office else "") or DEFAULT_FACEBOOK

        # Instagram: office -> default
        instagram = ((office.instagram_url or "").strip() if office else "") or DEFAULT_INSTAGRAM

        # LinkedIn: office -> default
        linkedin = ((office.linkedin_url or "").strip() if office else "") or DEFAULT_LINKEDIN

        return {
            "facebook_url": facebook,
            "instagram_url": instagram,
            "linkedin_url": linkedin,
        }

    @staticmethod
    def _render_template(
        template_content: str,
        employee: Employee,
        overrides: dict[str, str | None] | None = None,
    ) -> str:
        office = employee.office
        ovr = overrides or {}

        office_postal = ""
        if office and (office.postal_code or office.city):
            office_postal = f"{office.postal_code or ''} {office.city or ''}".strip()

        # Resolve phone — use override if provided
        phone_source = ovr.get("mobile_phone") or employee.phone
        formatted_phone = SignatureService._format_phone_number(phone_source)
        # Raw phone for tel: links (digits only, with country code)
        raw_phone = re.sub(r"\D", "", phone_source or "")
        if raw_phone and not raw_phone.startswith("47"):
            raw_phone = f"47{raw_phone}"  # Add Norwegian country code
        raw_phone = f"+{raw_phone}" if raw_phone else ""

        employee_photo_url = SignatureService._resolve_employee_photo_url(employee)
        social_urls = SignatureService._resolve_social_urls(employee)

        # Use employee's homepage URL if available, otherwise default to proaktiv.no
        employee_url = ovr.get("employee_url") or employee.homepage_profile_url or "https://proaktiv.no/"

        # Build Google Maps URL from full address
        office_address = (office.street_address or "") if office else ""
        full_address = f"{office_address}, {office_postal}".strip(", ")
        from urllib.parse import quote

        office_map_url = f"https://maps.google.com/?q={quote(full_address)}" if full_address else ""

        # HTML-escape text values to prevent broken rendering (e.g. & in names)
        # URLs are not escaped — they go into href attributes and must remain valid
        esc = html_lib.escape

        # Apply overrides: prefer override value (if non-null) over employee data
        display_name = ovr.get("display_name") or employee.full_name or ""
        job_title = ovr.get("job_title") or employee.title or ""
        email = ovr.get("email") or employee.email or ""
        office_name = ovr.get("office_name") or ((office.name or "") if office else "")

        replacements = {
            "{{DisplayName}}": esc(display_name),
            "{{JobTitle}}": esc(job_title),
            "{{MobilePhone}}": esc(formatted_phone),
            "{{MobilePhoneRaw}}": raw_phone,
            "{{Email}}": esc(email),
            "{{EmployeePhotoUrl}}": employee_photo_url,
            "{{EmployeeUrl}}": employee_url,
            "{{FacebookUrl}}": ovr.get("facebook_url") or social_urls["facebook_url"],
            "{{InstagramUrl}}": ovr.get("instagram_url") or social_urls["instagram_url"],
            "{{LinkedInUrl}}": ovr.get("linkedin_url") or social_urls["linkedin_url"],
            "{{OfficeName}}": esc(office_name),
            "{{OfficeAddress}}": esc(office_address),
            "{{OfficePostal}}": esc(office_postal),
            "{{OfficeMapUrl}}": office_map_url,
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

        # Load overrides if any exist
        from app.services.signature_override_service import SignatureOverrideService

        override = await SignatureOverrideService.get_by_employee_id(db, employee_id)
        overrides_dict = SignatureOverrideService.to_dict(override)

        template_path = SignatureService._resolve_template_path(version)
        try:
            template_content = template_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning("Signature template not found: %s", template_path)
            template_content = "<p>{{DisplayName}}<br>{{JobTitle}}<br>{{Email}}</p>"

        html_signature = SignatureService._render_template(template_content, employee, overrides_dict)
        text_signature = SignatureService._strip_html(html_signature)

        # Use overridden name/email in response if available
        display_name = (overrides_dict.get("display_name") if overrides_dict else None) or employee.full_name
        display_email = (overrides_dict.get("email") if overrides_dict else None) or employee.email or ""

        return {
            "html": html_signature,
            "text": text_signature,
            "employee_name": display_name,
            "employee_email": display_email,
        }
