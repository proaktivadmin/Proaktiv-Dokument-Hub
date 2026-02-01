"""
Signatures Router - API endpoints for email signature rendering.
"""

import base64
import html as html_lib
import logging
import os
import uuid as uuid_mod
from typing import Any, Literal
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.company_asset import CompanyAsset
from app.routers.auth import verify_session_token
from app.schemas.signature_override import SignatureOverrideResponse, SignatureOverrideUpdate
from app.services.employee_service import EmployeeService
from app.services.graph_service import GraphService
from app.services.image_service import ImageService
from app.services.signature_override_service import SignatureOverrideService
from app.services.signature_service import PLACEHOLDER_PHOTO, SignatureService

logger = logging.getLogger(__name__)

DEFAULT_SENDER_EMAIL = "froyland@proaktiv.no"
DEFAULT_FRONTEND_URL = "https://proaktiv-dokument-hub.vercel.app"

SignatureVersion = Literal["with-photo", "no-photo"]


class SignatureRenderResponse(BaseModel):
    """Rendered email signature response."""

    html: str = Field(..., description="HTML signature content")
    text: str = Field(..., description="Plain text signature content")
    employee_name: str = Field(..., description="Employee full name")
    employee_email: str = Field(..., description="Employee email address")


class SignatureSendRequest(BaseModel):
    """Optional request payload for sending signature email."""

    sender_email: str | None = Field(
        None,
        description="Override sender email (defaults to SIGNATURE_SENDER_EMAIL env var)",
    )


class SignatureSendResponse(BaseModel):
    """Signature email send response."""

    success: bool = Field(..., description="Whether the email was sent successfully")
    sent_to: str = Field(..., description="Recipient email address")
    message: str = Field(..., description="Result message")


router = APIRouter(prefix="/signatures", tags=["Signatures"])


def _require_auth(request: Request) -> None:
    settings = get_settings()
    if not settings.APP_PASSWORD_HASH:
        return

    token = request.cookies.get("session")
    if not token or not verify_session_token(token):
        raise HTTPException(status_code=401, detail="Not authenticated")


def _get_sender_email(payload: SignatureSendRequest | None) -> str:
    sender = (payload.sender_email.strip() if payload and payload.sender_email else "").strip()
    if not sender:
        sender = os.getenv("SIGNATURE_SENDER_EMAIL", "").strip()
    return sender or DEFAULT_SENDER_EMAIL


def _get_frontend_url() -> str:
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if not frontend_url:
        frontend_url = DEFAULT_FRONTEND_URL
    return frontend_url.rstrip("/")


def _render_notification_email(template: str, first_name: str, signature_url: str) -> str:
    safe_name = html_lib.escape(first_name or "")
    safe_url = html_lib.escape(signature_url)
    rendered = template.replace("{{FirstName}}", safe_name)
    return rendered.replace("{{SignatureUrl}}", safe_url)


@router.get("/{employee_id}", response_model=SignatureRenderResponse)
async def get_signature(
    employee_id: UUID,
    version: SignatureVersion = Query("with-photo", description="Signature version"),
    db: AsyncSession = Depends(get_db),
):
    """
    Render a personalized email signature for an employee.
    Only available for internal Proaktiv employees (not external contractors).
    """
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Only internal employees get signatures
    if employee.employee_type != "internal":
        raise HTTPException(status_code=403, detail="Signatures are only available for internal Proaktiv employees")

    signature = await SignatureService.render_signature(db, employee_id, version)
    if not signature:
        raise HTTPException(status_code=404, detail="Employee not found")
    return SignatureRenderResponse(**signature)


@router.post("/{employee_id}/send", response_model=SignatureSendResponse)
async def send_signature_email(
    employee_id: UUID,
    request: Request,
    payload: SignatureSendRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a signature notification email to the employee.
    Only available for internal Proaktiv employees (not external contractors).
    """
    _require_auth(request)

    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Only internal employees get signatures
    if employee.employee_type != "internal":
        raise HTTPException(status_code=403, detail="Signatures are only available for internal Proaktiv employees")

    if not employee.email:
        raise HTTPException(status_code=400, detail="Employee email not set")

    sender_email = _get_sender_email(payload)
    frontend_url = _get_frontend_url()
    signature_url = f"{frontend_url}/signature/{employee.id}"

    template_path = SignatureService.TEMPLATES_DIR / "signature-notification-email.html"
    try:
        template_content = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Signature notification template not found: %s", template_path)
        template_content = (
            "<p>Hei {{FirstName}},</p>"
            "<p>Signaturen din er klar.</p>"
            '<p><a href="{{SignatureUrl}}">{{SignatureUrl}}</a></p>'
            "<p>Hilsen<br>IT-avdelingen</p>"
        )

    greeting_name = employee.first_name or employee.full_name or "der"
    html_body = _render_notification_email(template_content, greeting_name, signature_url)

    subject = "Din e-postsignatur er klar"
    sent = await GraphService.send_mail(sender_email, employee.email, subject, html_body)
    message = "Signature email sent successfully" if sent else "Failed to send signature email"

    return SignatureSendResponse(success=sent, sent_to=employee.email, message=message)


@router.get("/{employee_id}/photo")
async def get_signature_photo(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return employee photo pre-cropped at 2x (160×192) for HiDPI email signatures."""
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    photo_url = (employee.profile_image_url or "").strip()
    if not photo_url or photo_url.startswith("/api/vitec"):
        photo_url = PLACEHOLDER_PHOTO

    # Handle asset:// URLs — serve photo from database metadata
    if photo_url.startswith("asset://"):
        asset_id = photo_url.replace("asset://", "")
        result = await db.execute(select(CompanyAsset).where(CompanyAsset.id == asset_id))
        asset = result.scalar_one_or_none()
        if asset and asset.metadata_json and asset.metadata_json.get("image_base64"):
            image_data = base64.b64decode(asset.metadata_json["image_base64"])
        else:
            logger.warning("Asset %s has no stored image data, falling back to placeholder", asset_id)
            photo_url = PLACEHOLDER_PHOTO
            image_data = None
    else:
        image_data = None

    if image_data is None:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(photo_url)
                resp.raise_for_status()
                image_data = resp.content
        except httpx.HTTPError:
            logger.warning("Failed to fetch photo for signature crop: %s", photo_url)
            raise HTTPException(status_code=502, detail="Could not fetch employee photo")

    cropped = ImageService.crop_for_signature(image_data, width=160, height=192)
    return Response(content=cropped, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


# --- Signature Override Endpoints (public, scoped by employee UUID) ---


@router.get("/{employee_id}/overrides", response_model=SignatureOverrideResponse | None)
async def get_signature_overrides(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get current signature overrides for an employee. Returns null if none exist."""
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    override = await SignatureOverrideService.get_by_employee_id(db, employee_id)
    if not override:
        return None
    return override


@router.put("/{employee_id}/overrides", response_model=SignatureOverrideResponse)
async def update_signature_overrides(
    employee_id: UUID,
    data: SignatureOverrideUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Create or update signature overrides for an employee (public, UUID-scoped)."""
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.employee_type != "internal":
        raise HTTPException(status_code=403, detail="Signatures are only available for internal employees")

    override = await SignatureOverrideService.upsert(db, employee_id, data)
    return override


@router.delete("/{employee_id}/overrides")
async def delete_signature_overrides(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Reset signature overrides (delete all overrides for an employee)."""
    deleted = await SignatureOverrideService.delete(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No overrides found for this employee")
    return {"success": True, "message": "Overrides reset to original values"}


# --- Photo Upload Endpoint (public, UUID-scoped) ---

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/{employee_id}/photo/upload")
async def upload_signature_photo(
    employee_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a new employee photo from the public signature page.

    The photo replaces the active profile_image_url. The old photo
    CompanyAsset record is preserved and remains visible in the
    admin dashboard employee files tab.
    """
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.employee_type != "internal":
        raise HTTPException(status_code=403, detail="Photo upload only available for internal employees")

    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Only JPEG and PNG images are accepted. Got: {file.content_type}",
        )

    # Read and validate size
    image_data = await file.read()
    if len(image_data) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="Image must be smaller than 5 MB")

    if len(image_data) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # Build WebDAV filename from employee email: froyland@proaktiv.no -> froyland@proaktiv_no.jpg
    email_for_filename = (employee.email or "").lower().replace(".", "_")
    webdav_filename = f"{email_for_filename}.jpg"
    webdav_path = f"/photos/employees/{webdav_filename}"
    public_photo_url = f"https://proaktiv.no/photos/employees/{webdav_filename.replace('@', '%40')}"

    # Store as CompanyAsset linked to employee
    asset_id = str(uuid_mod.uuid4())
    display_filename = file.filename or f"signature-photo-{asset_id}.jpg"

    # Try WebDAV upload to proaktiv.no/photos/employees/
    webdav_success = False
    try:
        from app.services.webdav_service import WebDAVService

        webdav = WebDAVService()
        await webdav.upload_file(webdav_path, image_data, "image/jpeg")
        webdav_success = True
        logger.info("Photo uploaded to WebDAV: %s", webdav_path)
    except Exception as e:
        logger.warning("WebDAV upload failed for signature photo: %s — storing in database", e)

    # Store image bytes as base64 in metadata when WebDAV unavailable
    asset_metadata: dict[str, Any] = {}
    if not webdav_success:
        asset_metadata["image_base64"] = base64.b64encode(image_data).decode("ascii")
        asset_metadata["content_type"] = file.content_type or "image/jpeg"

    # Create CompanyAsset record
    asset = CompanyAsset(
        id=asset_id,
        employee_id=str(employee_id),
        is_global=False,
        name=f"Signatur-bilde ({employee.full_name})",
        filename=display_filename,
        category="photo",
        content_type=file.content_type or "image/jpeg",
        file_size=len(image_data),
        storage_path=public_photo_url if webdav_success else webdav_path,
        metadata_json=asset_metadata if asset_metadata else None,
    )
    db.add(asset)

    # Update employee profile image URL
    if webdav_success:
        employee.profile_image_url = public_photo_url
    else:
        employee.profile_image_url = f"asset://{asset_id}"

    await db.commit()

    return {"success": True, "asset_id": asset_id, "message": "Photo uploaded successfully"}
