"""
Assets Router - API endpoints for company asset management.
"""

import io
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.company_asset import (
    CompanyAssetListResponse,
    CompanyAssetResponse,
    CompanyAssetUpdate,
)
from app.services.company_asset_service import CompanyAssetService
from app.services.webdav_service import WebDAVService

router = APIRouter(prefix="/assets", tags=["Assets"])


def _to_response(asset) -> CompanyAssetResponse:
    """Convert CompanyAsset model to response schema."""
    return CompanyAssetResponse(
        id=asset.id,
        name=asset.name,
        category=asset.category,
        office_id=asset.office_id,
        employee_id=asset.employee_id,
        is_global=asset.is_global,
        filename=asset.filename,
        content_type=asset.content_type,
        file_size=asset.file_size,
        storage_path=asset.storage_path,
        metadata_json=asset.metadata_json,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
        scope=asset.scope,
        is_image=asset.is_image,
        file_size_formatted=asset.file_size_formatted,
    )


@router.get("", response_model=CompanyAssetListResponse)
async def list_assets(
    category: str | None = Query(None, description="Filter by category"),
    office_id: UUID | None = Query(None, description="Filter by office"),
    employee_id: UUID | None = Query(None, description="Filter by employee"),
    is_global: bool | None = Query(None, description="Filter by global flag"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all assets with optional filtering.

    Category can be: logo, photo, marketing, document, other.
    """
    assets, total = await CompanyAssetService.list(
        db,
        category=category,
        office_id=office_id,
        employee_id=employee_id,
        is_global=is_global,
        skip=skip,
        limit=limit,
    )

    items = [_to_response(a) for a in assets]

    return CompanyAssetListResponse(items=items, total=total)


@router.post("/upload", response_model=CompanyAssetResponse, status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form("other"),
    office_id: str | None = Form(None),
    employee_id: str | None = Form(None),
    is_global: bool = Form(False),
    alt_text: str | None = Form(None),
    usage_notes: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a new asset.

    Files are stored in WebDAV under /assets/{scope}/{id}/.
    """
    # Determine scope and storage path
    scope = "global"
    scope_id = None
    if office_id:
        scope = "office"
        scope_id = office_id
    elif employee_id:
        scope = "employee"
        scope_id = employee_id

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Generate storage path
    import uuid as uuid_module

    asset_id = str(uuid_module.uuid4())
    storage_path = f"/assets/{scope}/{scope_id or 'company'}/{asset_id}_{file.filename}"

    # Upload to WebDAV (if available)
    try:
        webdav = WebDAVService()
        # Create directory structure
        await webdav.mkdir(f"/assets/{scope}/{scope_id or 'company'}")
        # Upload file
        await webdav.upload(storage_path, content)
    except Exception as e:
        # Log but don't fail - store path anyway for future upload
        import logging

        logging.warning(f"WebDAV upload failed: {e}")

    # Build metadata
    metadata = {}
    if alt_text:
        metadata["alt_text"] = alt_text
    if usage_notes:
        metadata["usage_notes"] = usage_notes

    # If image, try to get dimensions
    if file.content_type and file.content_type.startswith("image/"):
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(content))
            metadata["dimensions"] = {"width": img.width, "height": img.height}
        except Exception:
            pass

    # Create database record
    asset = await CompanyAssetService.create(
        db,
        name=name,
        filename=file.filename,
        category=category,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        storage_path=storage_path,
        office_id=UUID(office_id) if office_id else None,
        employee_id=UUID(employee_id) if employee_id else None,
        is_global=is_global,
        metadata=metadata,
    )

    return _to_response(asset)


@router.get("/{asset_id}", response_model=CompanyAssetResponse)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get an asset by ID.
    """
    asset = await CompanyAssetService.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return _to_response(asset)


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Download an asset file.
    """
    asset = await CompanyAssetService.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        webdav = WebDAVService()
        content = await webdav.download(asset.storage_path)

        return StreamingResponse(
            io.BytesIO(content),
            media_type=asset.content_type,
            headers={"Content-Disposition": f'attachment; filename="{asset.filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@router.put("/{asset_id}", response_model=CompanyAssetResponse)
async def update_asset(
    asset_id: UUID,
    data: CompanyAssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update asset metadata.

    Only name, category, and metadata can be updated.
    """
    asset = await CompanyAssetService.update(db, asset_id, data)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return _to_response(asset)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an asset.

    Removes both the database record and the file in storage.
    """
    asset = await CompanyAssetService.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Try to delete from WebDAV
    try:
        webdav = WebDAVService()
        await webdav.delete(asset.storage_path)
    except Exception as e:
        import logging

        logging.warning(f"Failed to delete file from WebDAV: {e}")

    # Delete database record
    await CompanyAssetService.delete(db, asset_id)
