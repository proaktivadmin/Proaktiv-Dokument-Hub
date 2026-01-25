"""
Vitec API Status and Connection Endpoints

Provides endpoints for checking Vitec Hub API configuration and connection status.
"""

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.config import settings
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vitec", tags=["Vitec"])


class VitecStatusResponse(BaseModel):
    """Response model for Vitec API status check."""

    configured: bool
    connected: bool
    installation_id: str | None = None
    error: str | None = None
    available_methods: list[str] | None = None


@router.get("/status", response_model=VitecStatusResponse)
async def get_vitec_status():
    """
    Check Vitec Hub API configuration and connection status.

    Returns:
        - configured: Whether credentials are present
        - connected: Whether a test API call succeeded
        - installation_id: The configured installation ID (masked)
        - error: Error message if connection failed
        - available_methods: Methods returned by Account/Methods if connected
    """
    hub = VitecHubService()

    # Check configuration
    if not hub.is_configured:
        return VitecStatusResponse(
            configured=False,
            connected=False,
            error="Vitec Hub credentials are not configured. Set VITEC_HUB_PRODUCT_LOGIN, VITEC_HUB_ACCESS_KEY, and VITEC_HUB_BASE_URL environment variables.",
        )

    # Get installation ID (masked for security)
    installation_id = settings.VITEC_INSTALLATION_ID
    masked_id = None
    if installation_id:
        # Show first 4 and last 4 characters
        if len(installation_id) > 8:
            masked_id = f"{installation_id[:4]}...{installation_id[-4:]}"
        else:
            masked_id = installation_id

    # Test connection by calling Account/Methods
    try:
        methods_data = await hub.get_methods()
        method_names = [m.get("name", str(m)) for m in methods_data] if methods_data else []

        return VitecStatusResponse(
            configured=True,
            connected=True,
            installation_id=masked_id,
            available_methods=method_names,
        )
    except HTTPException as e:
        logger.warning(f"Vitec Hub connection test failed: {e.detail}")
        return VitecStatusResponse(
            configured=True,
            connected=False,
            installation_id=masked_id,
            error=e.detail,
        )
    except Exception as e:
        logger.error(f"Unexpected error testing Vitec Hub connection: {e}")
        return VitecStatusResponse(
            configured=True,
            connected=False,
            installation_id=masked_id,
            error=f"Connection test failed: {str(e)}",
        )


@router.get("/employees/{employee_id}/picture")
async def get_employee_picture(
    employee_id: str,
    size: int | None = Query(None, ge=32, le=1024, description="Resize to square (32-1024px)"),
    crop: str = Query("top", description="Crop mode: top, center"),
):
    """
    DISABLED: Fetch employee profile picture from Vitec Hub.

    This endpoint is temporarily disabled to identify employees missing WebDAV photos.
    All employee photos should now be served from https://proaktiv.no/photos/employees/

    If you see broken images, the employee needs their photo uploaded to WebDAV.

    Supports optional resizing for avatars. When size is specified,
    the image is cropped to a square and resized.

    Args:
        employee_id: Vitec employee ID
        size: Optional size for square resize (e.g., 256 for 256x256)
        crop: Crop mode - "top" for portraits, "center" for general

    Returns:
        Image bytes with appropriate content-type
    """
    # DISABLED: Return 410 Gone to indicate this endpoint is deprecated
    raise HTTPException(
        status_code=410,
        detail="This endpoint is disabled. Employee photos are now served from WebDAV at https://proaktiv.no/photos/employees/. "
        "If you see this error, the employee's profile_image_url needs to be updated to the WebDAV URL.",
    )


@router.get("/departments/{department_id}/picture")
async def get_department_picture(department_id: str):
    """
    DISABLED: Fetch department banner/logo picture from Vitec Hub.

    This endpoint is temporarily disabled to identify offices missing WebDAV banners.
    All office banners should now be served from https://proaktiv.no/photos/offices/

    If you see broken images, the office needs their banner uploaded to WebDAV.

    Args:
        department_id: Vitec department ID

    Returns:
        Image bytes with appropriate content-type
    """
    # DISABLED: Return 410 Gone to indicate this endpoint is deprecated
    raise HTTPException(
        status_code=410,
        detail="This endpoint is disabled. Office banners are now served from WebDAV at https://proaktiv.no/photos/offices/. "
        "If you see this error, the office's banner_image_url needs to be updated to the WebDAV URL.",
    )


class SyncPicturesResponse(BaseModel):
    """Response model for picture sync operations."""

    total: int
    synced: int
    failed: int
    skipped: int


@router.post("/sync-office-pictures", response_model=SyncPicturesResponse)
async def sync_office_pictures():
    """
    Sync office banner pictures from Vitec Hub.

    Instead of storing base64 data (which fills up the database),
    we store a proxy URL that fetches images on-demand from Vitec API.
    """
    from sqlalchemy import select

    from app.database import get_db
    from app.models.office import Office

    hub = VitecHubService()
    installation_id = settings.VITEC_INSTALLATION_ID

    if not installation_id:
        raise HTTPException(
            status_code=500,
            detail="VITEC_INSTALLATION_ID is not configured.",
        )

    total = synced = failed = skipped = 0
    batch_size = 10  # Commit every 10 items

    async for db in get_db():
        result = await db.execute(select(Office).where(Office.vitec_department_id.isnot(None)))
        offices = result.scalars().all()
        total = len(offices)
        batch_count = 0

        for office in offices:
            if not office.vitec_department_id:
                skipped += 1
                continue

            try:
                # Check if Vitec has a picture for this department
                image_data = await hub.get_department_picture(installation_id, office.vitec_department_id)

                if image_data:
                    # Store proxy URL instead of base64 data
                    # This URL will fetch the image on-demand from our API
                    proxy_url = f"/api/vitec/departments/{office.vitec_department_id}/picture"
                    office.banner_image_url = proxy_url
                    synced += 1
                    batch_count += 1
                else:
                    skipped += 1

            except Exception as e:
                logger.error(f"Failed to check picture for office {office.id}: {e}")
                failed += 1

            # Commit in batches
            if batch_count >= batch_size:
                await db.commit()
                batch_count = 0

        # Commit any remaining changes
        if batch_count > 0:
            await db.commit()
        break

    return SyncPicturesResponse(
        total=total,
        synced=synced,
        failed=failed,
        skipped=skipped,
    )


@router.post("/sync-employee-pictures", response_model=SyncPicturesResponse)
async def sync_employee_pictures():
    """
    Sync employee profile pictures from Vitec Hub.

    Instead of storing base64 data (which fills up the database),
    we store a proxy URL that fetches images on-demand from Vitec API.
    """
    from sqlalchemy import select

    from app.database import get_db
    from app.models.employee import Employee

    hub = VitecHubService()
    installation_id = settings.VITEC_INSTALLATION_ID

    if not installation_id:
        raise HTTPException(
            status_code=500,
            detail="VITEC_INSTALLATION_ID is not configured.",
        )

    total = synced = failed = skipped = 0
    batch_size = 10  # Commit every 10 items

    async for db in get_db():
        result = await db.execute(select(Employee).where(Employee.vitec_employee_id.isnot(None)))
        employees = result.scalars().all()
        total = len(employees)
        batch_count = 0

        for employee in employees:
            if not employee.vitec_employee_id:
                skipped += 1
                continue

            try:
                # Check if Vitec has a picture for this employee
                image_data = await hub.get_employee_picture(installation_id, employee.vitec_employee_id)

                if image_data:
                    # Store proxy URL instead of base64 data
                    # This URL will fetch the image on-demand from our API
                    proxy_url = f"/api/vitec/employees/{employee.vitec_employee_id}/picture"
                    employee.profile_image_url = proxy_url
                    synced += 1
                    batch_count += 1
                else:
                    skipped += 1

            except Exception as e:
                logger.error(f"Failed to check picture for employee {employee.id}: {e}")
                failed += 1

            # Commit in batches
            if batch_count >= batch_size:
                await db.commit()
                batch_count = 0

        # Commit any remaining changes
        if batch_count > 0:
            await db.commit()
        break

    return SyncPicturesResponse(
        total=total,
        synced=synced,
        failed=failed,
        skipped=skipped,
    )
