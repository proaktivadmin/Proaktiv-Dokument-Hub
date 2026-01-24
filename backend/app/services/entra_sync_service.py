"""
Entra ID Sync Service - Business logic for syncing employees to Microsoft Entra ID.

This service provides methods to:
1. Preview what would change when syncing an employee
2. Generate email signature previews
3. Sync employee profiles to Entra ID
4. Upload photos to Entra ID
5. Push email signatures to Exchange Online

Note: The actual sync is performed via the PowerShell script for full functionality.
This service provides preview and status functionality for the UI.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.employee import Employee
from app.schemas.entra_sync import (
    EntraConnectionStatus,
    EntraImportResult,
    EntraSyncBatchResult,
    EntraSyncPreview,
    EntraSyncResult,
    PropertyChange,
    RoamingSignaturesStatus,
    SignaturePreview,
    SyncScope,
)

logger = logging.getLogger(__name__)


class EntraSyncService:
    """Service for Entra ID sync operations."""

    # Template directory path
    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "scripts" / "templates"
    IMPORT_SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "import_entra_employees.py"

    @staticmethod
    def is_enabled() -> bool:
        """Check if Entra ID sync is enabled in configuration."""
        # Check for required environment variables
        tenant_id = os.environ.get("ENTRA_TENANT_ID") or getattr(settings, "ENTRA_TENANT_ID", None)
        client_id = os.environ.get("ENTRA_CLIENT_ID") or getattr(settings, "ENTRA_CLIENT_ID", None)

        return bool(tenant_id and client_id)

    @staticmethod
    def get_connection_status() -> EntraConnectionStatus:
        """Get the current Entra ID connection status."""
        tenant_id = os.environ.get("ENTRA_TENANT_ID") or getattr(settings, "ENTRA_TENANT_ID", None)
        client_id = os.environ.get("ENTRA_CLIENT_ID") or getattr(settings, "ENTRA_CLIENT_ID", None)

        enabled = bool(tenant_id and client_id)

        # Mask IDs for security
        masked_tenant = f"{tenant_id[:8]}...{tenant_id[-4:]}" if tenant_id and len(tenant_id) > 12 else None
        masked_client = f"{client_id[:8]}...{client_id[-4:]}" if client_id and len(client_id) > 12 else None

        # Note: We can't actually test connection without making API calls
        # For now, we report "connected" if credentials are configured
        return EntraConnectionStatus(
            connected=enabled,
            enabled=enabled,
            tenant_id=masked_tenant,
            client_id=masked_client,
            error=None if enabled else "Entra ID credentials not configured",
        )

    @staticmethod
    def get_roaming_signatures_status() -> RoamingSignaturesStatus:
        """Get roaming signatures status.

        Note: This would require an Exchange Online connection to check properly.
        For now, we return a warning that users should verify manually.
        """
        return RoamingSignaturesStatus(
            enabled=False,  # We can't check without Exchange connection
            warning=(
                "Unable to check roaming signatures status. "
                "If roaming signatures are enabled in your organization, "
                "server-side signatures may be overridden by client signatures."
            ),
        )

    @staticmethod
    def import_entra_employees(*, dry_run: bool = False, filter_email: str | None = None) -> EntraImportResult:
        """Import Entra ID users into local database (read-only to Entra)."""
        script_path = EntraSyncService.IMPORT_SCRIPT_PATH
        if not script_path.exists():
            return EntraImportResult(
                success=False,
                dry_run=dry_run,
                error=f"Import script not found at {script_path}",
            )

        env = os.environ.copy()
        if settings.DATABASE_URL and not env.get("DATABASE_URL"):
            env["DATABASE_URL"] = settings.DATABASE_URL
        if settings.ENTRA_TENANT_ID and not env.get("ENTRA_TENANT_ID"):
            env["ENTRA_TENANT_ID"] = settings.ENTRA_TENANT_ID
        if settings.ENTRA_CLIENT_ID and not env.get("ENTRA_CLIENT_ID"):
            env["ENTRA_CLIENT_ID"] = settings.ENTRA_CLIENT_ID
        if settings.ENTRA_CLIENT_SECRET and not env.get("ENTRA_CLIENT_SECRET"):
            env["ENTRA_CLIENT_SECRET"] = settings.ENTRA_CLIENT_SECRET

        if not env.get("ENTRA_TENANT_ID") or not env.get("ENTRA_CLIENT_ID"):
            return EntraImportResult(
                success=False,
                dry_run=dry_run,
                error="ENTRA_TENANT_ID and ENTRA_CLIENT_ID must be configured",
            )
        if not env.get("ENTRA_CLIENT_SECRET"):
            return EntraImportResult(
                success=False,
                dry_run=dry_run,
                error="ENTRA_CLIENT_SECRET must be configured for Entra import",
            )

        cmd = [sys.executable, str(script_path), "--json"]
        if dry_run:
            cmd.append("--dry-run")
        if filter_email:
            cmd.extend(["--filter-email", filter_email])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(script_path.parent.parent),
                env=env,
            )
        except subprocess.TimeoutExpired:
            return EntraImportResult(success=False, dry_run=dry_run, error="Import timed out after 5 minutes")
        except Exception as exc:
            logger.exception("Error running Entra import")
            return EntraImportResult(success=False, dry_run=dry_run, error=str(exc))

        if result.returncode != 0:
            error_message = result.stderr.strip() or result.stdout.strip() or "Import failed"
            return EntraImportResult(success=False, dry_run=dry_run, error=error_message)

        try:
            payload = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return EntraImportResult(
                success=False,
                dry_run=dry_run,
                error="Import completed but returned invalid JSON",
            )

        return EntraImportResult(
            success=True,
            dry_run=payload.get("dry_run", False),
            employees_loaded=payload.get("employees_loaded"),
            matched_updated=payload.get("matched_updated"),
            employees_not_matched=payload.get("employees_not_matched"),
            entra_users_not_matched=payload.get("entra_users_not_matched"),
            error=None,
        )

    @staticmethod
    async def get_employee_with_office(db: AsyncSession, employee_id: UUID) -> Employee | None:
        """Get an employee with office data loaded."""
        result = await db.execute(
            select(Employee).options(selectinload(Employee.office)).where(Employee.id == str(employee_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_sync_preview(db: AsyncSession, employee_id: UUID) -> EntraSyncPreview | None:
        """Generate a preview of what would change when syncing an employee.

        This compares the local database data with what we expect in Entra ID.
        Note: For a true comparison, we would need to call the Graph API.
        For now, we show what would be pushed from the database.
        """
        employee = await EntraSyncService.get_employee_with_office(db, employee_id)
        if not employee:
            return None

        # Build property changes (what we would push)
        changes: list[PropertyChange] = []

        # Display name
        display_name = f"{employee.first_name} {employee.last_name}".strip()
        changes.append(
            PropertyChange(
                property="displayName",
                current_value=None,  # Would need Graph API call
                new_value=display_name,
                will_update=bool(display_name),
            )
        )

        # Given name
        changes.append(
            PropertyChange(
                property="givenName",
                current_value=None,
                new_value=employee.first_name,
                will_update=bool(employee.first_name),
            )
        )

        # Surname
        changes.append(
            PropertyChange(
                property="surname",
                current_value=None,
                new_value=employee.last_name,
                will_update=bool(employee.last_name),
            )
        )

        # Job title
        if employee.title:
            changes.append(
                PropertyChange(
                    property="jobTitle",
                    current_value=None,
                    new_value=employee.title,
                    will_update=True,
                )
            )

        # Mobile phone
        if employee.phone:
            changes.append(
                PropertyChange(
                    property="mobilePhone",
                    current_value=None,
                    new_value=employee.phone,
                    will_update=True,
                )
            )

        # Department (office name)
        if employee.office and employee.office.name:
            changes.append(
                PropertyChange(
                    property="department",
                    current_value=None,
                    new_value=employee.office.name,
                    will_update=True,
                )
            )

        # Office location (city)
        if employee.office and employee.office.city:
            changes.append(
                PropertyChange(
                    property="officeLocation",
                    current_value=None,
                    new_value=employee.office.city,
                    will_update=True,
                )
            )

        # Street address
        if employee.office and employee.office.street_address:
            changes.append(
                PropertyChange(
                    property="streetAddress",
                    current_value=None,
                    new_value=employee.office.street_address,
                    will_update=True,
                )
            )

        # Postal code
        if employee.office and employee.office.postal_code:
            changes.append(
                PropertyChange(
                    property="postalCode",
                    current_value=None,
                    new_value=employee.office.postal_code,
                    will_update=True,
                )
            )

        return EntraSyncPreview(
            employee_id=employee.id,
            employee_name=employee.full_name,
            employee_email=employee.email,
            entra_user_found=True,  # Assume found (would need API call to verify)
            entra_user_id=None,  # Would need API call
            entra_upn=employee.email,
            profile_changes=changes,
            photo_needs_update=bool(employee.profile_image_url),
            photo_url=employee.profile_image_url,
            signature_preview_available=True,
        )

    @staticmethod
    def _render_template(template_content: str, employee: Employee) -> str:
        """Render a template with employee data."""
        office = employee.office

        replacements = {
            "{{DisplayName}}": f"{employee.first_name} {employee.last_name}".strip(),
            "{{JobTitle}}": employee.title or "",
            "{{Email}}": employee.email or "",
            "{{MobilePhone}}": employee.phone or "",
            "{{OfficeName}}": office.name if office else "",
            "{{OfficeAddress}}": office.street_address if office else "",
            "{{OfficePostal}}": f"{office.postal_code} {office.city}".strip() if office else "",
            "{{OfficePhone}}": office.phone if office else "",
            "{{OfficeEmail}}": office.email if office else "",
            "{{ProfileUrl}}": employee.profile_image_url or "",
        }

        result = template_content
        for key, value in replacements.items():
            result = result.replace(key, value or "")

        return result

    @staticmethod
    async def generate_signature_preview(db: AsyncSession, employee_id: UUID) -> SignaturePreview | None:
        """Generate an email signature preview for an employee."""
        employee = await EntraSyncService.get_employee_with_office(db, employee_id)
        if not employee:
            return None

        # Load templates
        html_template_path = EntraSyncService.TEMPLATES_DIR / "email-signature.html"
        txt_template_path = EntraSyncService.TEMPLATES_DIR / "email-signature.txt"

        try:
            html_content = html_template_path.read_text(encoding="utf-8")
            html_signature = EntraSyncService._render_template(html_content, employee)
        except FileNotFoundError:
            html_signature = f"<p>{employee.full_name}<br>{employee.title or ''}<br>{employee.email or ''}</p>"

        try:
            txt_content = txt_template_path.read_text(encoding="utf-8")
            text_signature = EntraSyncService._render_template(txt_content, employee)
        except FileNotFoundError:
            text_signature = f"{employee.full_name}\n{employee.title or ''}\n{employee.email or ''}"

        return SignaturePreview(
            employee_id=employee.id,
            employee_name=employee.full_name,
            html=html_signature,
            text=text_signature,
        )

    @staticmethod
    async def sync_employee(
        db: AsyncSession,
        employee_id: UUID,
        scope: list[SyncScope],
        dry_run: bool = False,
    ) -> EntraSyncResult:
        """Sync a single employee to Entra ID.

        This method calls the PowerShell script to perform the actual sync.
        For production use, the script should be run with proper credentials.
        """
        employee = await EntraSyncService.get_employee_with_office(db, employee_id)
        if not employee:
            return EntraSyncResult(
                success=False,
                employee_id=employee_id,
                employee_name="Unknown",
                error="Employee not found",
            )

        if not employee.email:
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="Employee has no email address",
            )

        # Check if Entra sync is enabled
        if not EntraSyncService.is_enabled():
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="Entra ID sync is not configured. Set ENTRA_TENANT_ID and ENTRA_CLIENT_ID.",
            )

        # Build PowerShell command
        script_path = Path(__file__).parent.parent.parent / "scripts" / "Sync-EntraIdEmployees.ps1"

        if not script_path.exists():
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="Sync script not found",
            )

        # Get credentials from environment
        tenant_id = os.environ.get("ENTRA_TENANT_ID")
        client_id = os.environ.get("ENTRA_CLIENT_ID")
        organization = os.environ.get("ENTRA_ORGANIZATION")
        cert_thumbprint = os.environ.get("ENTRA_CERT_THUMBPRINT")
        client_secret = os.environ.get("ENTRA_CLIENT_SECRET")

        if not organization:
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="ENTRA_ORGANIZATION environment variable not set",
            )

        # Build command
        cmd = [
            "pwsh",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-TenantId",
            tenant_id,
            "-ClientId",
            client_id,
            "-Organization",
            organization,
            "-FilterEmail",
            employee.email,
        ]

        # Add auth method
        if cert_thumbprint:
            cmd.extend(["-CertificateThumbprint", cert_thumbprint])
        elif client_secret:
            # Client secret is passed via environment variable
            pass
        else:
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="No authentication method configured (certificate or secret)",
            )

        # Add scope flags
        if "profile" not in scope:
            cmd.append("-SkipProfile")
        if "photo" not in scope:
            cmd.append("-SkipPhoto")
        if "signature" not in scope:
            cmd.append("-SkipSignature")

        if dry_run:
            cmd.append("-DryRun")

        cmd.append("-Force")  # Skip confirmation

        try:
            # Run the PowerShell script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=str(script_path.parent.parent),  # backend directory
            )

            success = result.returncode == 0

            return EntraSyncResult(
                success=success,
                employee_id=employee.id,
                employee_name=employee.full_name,
                entra_user_id=None,  # Would need to parse from output
                profile_updated="profile" in scope and success,
                photo_updated="photo" in scope and success,
                signature_pushed="signature" in scope and success,
                error=result.stderr if not success else None,
            )

        except subprocess.TimeoutExpired:
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="Sync timed out after 2 minutes",
            )
        except FileNotFoundError:
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error="PowerShell (pwsh) not found. Install PowerShell 7+.",
            )
        except Exception as e:
            logger.exception(f"Error syncing employee {employee_id}")
            return EntraSyncResult(
                success=False,
                employee_id=employee.id,
                employee_name=employee.full_name,
                error=str(e),
            )

    @staticmethod
    async def sync_batch(
        db: AsyncSession,
        employee_ids: list[UUID],
        scope: list[SyncScope],
        dry_run: bool = False,
    ) -> EntraSyncBatchResult:
        """Sync multiple employees to Entra ID."""
        results: list[EntraSyncResult] = []
        successful = 0
        failed = 0
        skipped = 0
        profiles_updated = 0
        photos_uploaded = 0
        signatures_pushed = 0

        for employee_id in employee_ids:
            result = await EntraSyncService.sync_employee(db, employee_id, scope, dry_run)
            results.append(result)

            if result.success:
                successful += 1
                if result.profile_updated:
                    profiles_updated += 1
                if result.photo_updated:
                    photos_uploaded += 1
                if result.signature_pushed:
                    signatures_pushed += 1
            elif result.error and "not found" in result.error.lower():
                skipped += 1
            else:
                failed += 1

        return EntraSyncBatchResult(
            total=len(employee_ids),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            profiles_updated=profiles_updated,
            photos_uploaded=photos_uploaded,
            signatures_pushed=signatures_pushed,
        )
