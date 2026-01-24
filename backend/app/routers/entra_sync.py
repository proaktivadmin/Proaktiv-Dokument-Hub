"""
Entra ID Sync Router - API endpoints for Entra ID sync operations.

Provides endpoints for:
- Preview sync changes for an employee
- Generate email signature previews
- Sync single employee to Entra ID
- Batch sync multiple employees
- Check connection status
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.entra_sync import (
    EntraConnectionStatus,
    EntraImportRequest,
    EntraImportResult,
    EntraOfficeImportRequest,
    EntraOfficeImportResult,
    EntraSyncBatchRequest,
    EntraSyncBatchResult,
    EntraSyncPreview,
    EntraSyncRequest,
    EntraSyncResult,
    RoamingSignaturesStatus,
    SignaturePreview,
)
from app.services.entra_sync_service import EntraSyncService

router = APIRouter(prefix="/entra-sync", tags=["Entra Sync"])


@router.get("/status", response_model=EntraConnectionStatus)
async def get_status():
    """
    Get Entra ID connection status.

    Returns whether Entra ID sync is enabled and configured.
    """
    return EntraSyncService.get_connection_status()


@router.get("/roaming-signatures", response_model=RoamingSignaturesStatus)
async def get_roaming_signatures_status():
    """
    Get roaming signatures status.

    Returns whether roaming signatures are enabled in Exchange Online.
    Note: This requires an active Exchange connection to check properly.
    """
    return EntraSyncService.get_roaming_signatures_status()


@router.post("/import", response_model=EntraImportResult)
async def import_entra_employees(request: EntraImportRequest):
    """
    Import Entra ID users into the local database (read-only to Entra).

    Writes only to local database; Entra is never modified.
    """
    result = EntraSyncService.import_entra_employees(
        dry_run=request.dry_run,
        filter_email=request.filter_email,
    )
    return result


@router.post("/import-offices", response_model=EntraOfficeImportResult)
async def import_entra_offices(request: EntraOfficeImportRequest):
    """
    Import Entra ID M365 Groups into the local office database (read-only to Entra).

    Fetches M365 Groups from Microsoft Graph, matches them to local offices,
    and stores the Entra data in secondary columns. Vitec data is never modified.
    """
    result = EntraSyncService.import_entra_offices(
        dry_run=request.dry_run,
        filter_office_id=str(request.filter_office_id) if request.filter_office_id else None,
        fetch_details=request.fetch_details if hasattr(request, "fetch_details") else False,
    )
    return result


@router.get("/preview/{employee_id}", response_model=EntraSyncPreview)
async def get_sync_preview(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a preview of what would change when syncing an employee.

    Returns a comparison of local database values vs Entra ID.
    Note: Current Entra ID values are not fetched (would require API call).
    """
    preview = await EntraSyncService.get_sync_preview(db, employee_id)
    if not preview:
        raise HTTPException(status_code=404, detail="Employee not found")
    return preview


@router.get("/signature-preview/{employee_id}", response_model=SignaturePreview)
async def get_signature_preview(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an email signature preview for an employee.

    Returns the rendered HTML and plain text signatures.
    """
    preview = await EntraSyncService.generate_signature_preview(db, employee_id)
    if not preview:
        raise HTTPException(status_code=404, detail="Employee not found")
    return preview


@router.post("/push/{employee_id}", response_model=EntraSyncResult)
async def push_employee(
    employee_id: UUID,
    request: EntraSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Sync a single employee to Entra ID.

    Pushes profile data, photo, and/or email signature based on the scope.
    Use dry_run=true to preview changes without applying them.
    """
    if not EntraSyncService.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Entra ID sync is not configured. Set ENTRA_TENANT_ID and ENTRA_CLIENT_ID.",
        )

    result = await EntraSyncService.sync_employee(
        db,
        employee_id,
        request.scope,
        request.dry_run,
    )
    return result


@router.post("/push-batch", response_model=EntraSyncBatchResult)
async def push_batch(
    request: EntraSyncBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Sync multiple employees to Entra ID.

    Pushes profile data, photo, and/or email signatures for all specified employees.
    Use dry_run=true to preview changes without applying them.
    """
    if not EntraSyncService.is_enabled():
        raise HTTPException(
            status_code=503,
            detail="Entra ID sync is not configured. Set ENTRA_TENANT_ID and ENTRA_CLIENT_ID.",
        )

    if len(request.employee_ids) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 employees per batch. Please split into smaller batches.",
        )

    result = await EntraSyncService.sync_batch(
        db,
        request.employee_ids,
        request.scope,
        request.dry_run,
    )
    return result
