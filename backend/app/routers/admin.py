"""
Admin Router - Administrative endpoints for migration and maintenance.

These endpoints are for one-time operations and should be protected in production.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pathlib import Path
from typing import Optional
import logging

from app.database import get_db
from app.models.template import Template

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)


@router.post("/import-templates")
async def import_templates_from_library(
    library_path: str = "library",
    db: AsyncSession = Depends(get_db)
) -> dict:
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
        raise HTTPException(
            status_code=400,
            detail=f"Library path not found: {library_path}"
        )
    
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
                content = file_path.read_text(encoding='utf-8')
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
        "total_templates": len(templates)
    }


@router.get("/template-content-stats")
async def get_template_content_stats(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get statistics about template content storage.
    
    Returns counts of templates with and without content stored in database.
    """
    # Count total templates
    total_result = await db.execute(
        select(func.count(Template.id))
    )
    total = total_result.scalar() or 0
    
    # Count templates with content
    with_content_result = await db.execute(
        select(func.count(Template.id)).where(Template.content.isnot(None))
    )
    with_content = with_content_result.scalar() or 0
    
    # Count templates without content
    without_content = total - with_content
    
    return {
        "total_templates": total,
        "with_content": with_content,
        "without_content": without_content,
        "percentage_complete": round((with_content / total * 100), 1) if total > 0 else 0
    }


def find_template_file(library_path: Path, file_name: str) -> Optional[Path]:
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
    if not file_name.endswith('.html'):
        html_name = f"{file_name}.html"
        for path in library_path.rglob(html_name):
            return path
    
    # Try matching by title (remove extension, match loosely)
    base_name = Path(file_name).stem
    for path in library_path.rglob("*.html"):
        if base_name.lower() in path.stem.lower():
            return path
    
    return None
