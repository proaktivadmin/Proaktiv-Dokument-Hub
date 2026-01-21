"""
Admin Router - Administrative endpoints for migration and maintenance.

These endpoints are for one-time operations and should be protected in production.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.template import Template
from app.services.azure_storage_service import get_azure_storage_service

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)


@router.post("/import-templates")
async def import_templates_from_library(library_path: str = "library", db: AsyncSession = Depends(get_db)) -> dict:
    """
    One-time import: Read HTML files from library/ and store in database.

    This endpoint imports template content from the local file system
    into the database. Only imports templates where content is currently NULL.

    Use this during migration from Azure Blob Storage to database storage.

    Args:
        library_path: Path to library folder (default: "library")

    Returns:
        Dict with import statistics
    """
    lib_path = Path(library_path)

    if not lib_path.exists():
        raise HTTPException(status_code=400, detail=f"Library path not found: {library_path}")

    imported = 0
    skipped = 0
    already_has_content = 0
    errors = []

    # Get all templates
    result = await db.execute(select(Template))
    templates = result.scalars().all()

    for template in templates:
        # Skip if already has content
        if template.content:
            already_has_content += 1
            continue

        try:
            # Try to find matching file
            file_path = find_template_file(lib_path, template.file_name)

            if file_path and file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                template.content = content
                imported += 1
                logger.info(f"Imported: {template.file_name} ({len(content)} chars)")
            else:
                skipped += 1
                logger.warning(f"File not found: {template.file_name}")

        except Exception as e:
            error_msg = f"{template.file_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Import error: {error_msg}")

    await db.commit()

    logger.info(
        f"Import complete: {imported} imported, "
        f"{already_has_content} already had content, "
        f"{skipped} skipped, {len(errors)} errors"
    )

    return {
        "imported": imported,
        "already_has_content": already_has_content,
        "skipped": skipped,
        "errors": errors,
        "total_templates": len(templates),
    }


@router.get("/template-content-stats")
async def get_template_content_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Get statistics about template content storage.

    Returns counts of templates with and without content stored in database.
    """
    # Count total templates
    total_result = await db.execute(select(func.count(Template.id)))
    total = total_result.scalar() or 0

    # Count templates with content
    with_content_result = await db.execute(select(func.count(Template.id)).where(Template.content.isnot(None)))
    with_content = with_content_result.scalar() or 0

    # Count templates without content
    without_content = total - with_content

    return {
        "total_templates": total,
        "with_content": with_content,
        "without_content": without_content,
        "percentage_complete": round((with_content / total * 100), 1) if total > 0 else 0,
    }


@router.post("/sync-from-azure")
async def sync_templates_from_azure(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Sync templates from Azure Blob Storage to the database.

    This endpoint:
    1. Lists all blobs in the templates container
    2. For each blob not already in the database, creates a template entry
    3. Downloads and stores HTML content for HTML templates

    Use this to populate the database after a fresh deployment.
    """
    storage = get_azure_storage_service()

    if not storage.is_configured:
        raise HTTPException(status_code=503, detail="Azure Storage not configured")

    # List all blobs in templates container
    blobs = await storage.list_blobs()

    created = 0
    skipped = 0
    errors = []

    for blob in blobs:
        blob_name = blob["name"]

        # Check if template already exists by file_name
        existing = await db.execute(select(Template).where(Template.file_name == blob_name))
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        try:
            # Determine file type
            file_ext = blob_name.split(".")[-1].lower() if "." in blob_name else "unknown"

            # Create title from filename
            title = Path(blob_name).stem.replace("_", " ").replace("-", " ").title()

            # Download content for HTML files
            content = None
            if file_ext in ["html", "htm"]:
                content_bytes = await storage.download_file(blob_name)
                if content_bytes:
                    try:
                        content = content_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        content = content_bytes.decode("latin-1")

            # Create template entry
            template = Template(
                title=title,
                file_name=blob_name,
                file_type=file_ext,
                file_size_bytes=blob["size"] or 0,
                azure_blob_url=f"https://{storage.client.account_name}.blob.core.windows.net/templates/{blob_name}",
                azure_blob_container="templates",
                status="published",
                created_by="system@proaktiv.no",
                updated_by="system@proaktiv.no",
                content=content,
            )

            db.add(template)
            created += 1
            logger.info(f"Synced template: {blob_name}")

        except Exception as e:
            error_msg = f"{blob_name}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Sync error: {error_msg}")

    await db.commit()

    logger.info(f"Sync complete: {created} created, {skipped} skipped, {len(errors)} errors")

    return {"created": created, "skipped": skipped, "errors": errors, "total_blobs": len(blobs)}


def find_template_file(library_path: Path, file_name: str) -> Path | None:
    """
    Find template file, searching subdirectories.

    Args:
        library_path: Base library path
        file_name: Name of the file to find

    Returns:
        Path to file if found, None otherwise
    """
    # Direct match in root
    direct = library_path / file_name
    if direct.exists():
        return direct

    # Search subdirectories
    for path in library_path.rglob(file_name):
        return path

    # Try with .html extension if not already
    if not file_name.endswith(".html"):
        html_name = f"{file_name}.html"
        for path in library_path.rglob(html_name):
            return path

    # Try matching by title (remove extension, match loosely)
    base_name = Path(file_name).stem
    for path in library_path.rglob("*.html"):
        if base_name.lower() in path.stem.lower():
            return path

    return None
