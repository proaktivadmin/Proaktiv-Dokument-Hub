"""
Template API Routes

Handles all template CRUD operations with database integration.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.template_service import TemplateService
from app.services.audit_service import AuditService
from app.config import get_mock_user

router = APIRouter()


# Pydantic schemas for request bodies
class TemplateUpdateRequest(BaseModel):
    """Request body for updating a template."""
    title: Optional[str] = Field(None, max_length=255, description="Template title")
    description: Optional[str] = Field(None, max_length=2000, description="Template description")
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$", description="Template status")


def get_current_user():
    """Get current user (mocked for Phase 1)."""
    return get_mock_user()


@router.get("")
async def list_templates(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
):
    """List all templates with filtering and pagination."""
    templates, total = await TemplateService.get_list(
        db,
        status=status,
        search=search,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return {
        "templates": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "file_name": t.file_name,
                "file_type": t.file_type,
                "file_size_bytes": t.file_size_bytes,
                "status": t.status,
                "version": t.version,
                "preview_url": t.preview_url,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "tags": [{"id": str(tag.id), "name": tag.name, "color": tag.color} for tag in t.tags],
                "categories": [{"id": str(cat.id), "name": cat.name, "icon": cat.icon} for cat in t.categories],
            }
            for t in templates
        ],
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if total > 0 else 0
        }
    }


@router.get("/{template_id}")
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a single template by ID."""
    template = await TemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": str(template.id),
        "title": template.title,
        "description": template.description,
        "file_name": template.file_name,
        "file_type": template.file_type,
        "file_size_bytes": template.file_size_bytes,
        "azure_blob_url": template.azure_blob_url,
        "azure_blob_container": template.azure_blob_container,
        "status": template.status,
        "version": template.version,
        "created_by": template.created_by,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_by": template.updated_by,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
        "published_at": template.published_at.isoformat() if template.published_at else None,
        "preview_url": template.preview_url,
        "page_count": template.page_count,
        "language": template.language,
        "vitec_merge_fields": template.vitec_merge_fields or [],
        "tags": [{"id": str(tag.id), "name": tag.name, "color": tag.color} for tag in template.tags],
        "categories": [{"id": str(cat.id), "name": cat.name, "icon": cat.icon} for cat in template.categories],
    }


@router.post("", status_code=201)
async def create_template(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("draft"),
    user: dict = Depends(get_current_user)
):
    """Upload a new template."""
    # Validate file type
    allowed_types = ["docx", "doc", "pdf", "xlsx", "xls"]
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read file
    file_content = await file.read()
    file_size = len(file_content)
    
    # TODO: Upload to Azure Blob Storage
    # For now, use a mock URL
    blob_url = f"mock://templates/{file.filename}"
    
    # Create template
    template = await TemplateService.create(
        db,
        title=title,
        description=description,
        file_name=file.filename,
        file_type=file_ext,
        file_size_bytes=file_size,
        azure_blob_url=blob_url,
        created_by=user["email"],
        status=status
    )
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template.id,
        action="created",
        user_email=user["email"],
        details={"title": title, "file_name": file.filename}
    )
    
    return {
        "id": str(template.id),
        "title": template.title,
        "file_name": template.file_name,
        "status": template.status,
        "created_at": template.created_at.isoformat() if template.created_at else None
    }


@router.put("/{template_id}")
async def update_template(
    template_id: UUID,
    body: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Update template metadata."""
    template = await TemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updates = {}
    if body.title is not None:
        updates["title"] = body.title
    if body.description is not None:
        updates["description"] = body.description
    if body.status is not None:
        updates["status"] = body.status
        if body.status == "published":
            updates["published_at"] = datetime.now(timezone.utc)
    
    template = await TemplateService.update(
        db,
        template,
        updated_by=user["email"],
        **updates
    )
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template.id,
        action="updated",
        user_email=user["email"],
        details=updates
    )
    
    return {
        "id": str(template.id),
        "title": template.title,
        "status": template.status,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None
    }


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Archive a template (soft delete)."""
    template = await TemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await TemplateService.delete(db, template)
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template.id,
        action="deleted",
        user_email=user["email"]
    )
    
    return None


@router.get("/{template_id}/download")
async def download_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get download URL for template."""
    template = await TemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template.id,
        action="downloaded",
        user_email=user["email"]
    )
    
    # TODO: Generate SAS URL for Azure Blob Storage
    return {
        "download_url": template.azure_blob_url,
        "file_name": template.file_name,
        "expires_at": datetime.now(timezone.utc).isoformat()
    }

