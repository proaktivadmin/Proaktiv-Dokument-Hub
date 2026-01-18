"""
Template API Routes

Handles all template CRUD operations with database integration.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.template_service import TemplateService
from app.services.audit_service import AuditService
from app.services.azure_storage_service import get_azure_storage_service
from app.services.sanitizer_service import get_sanitizer_service
from app.services.template_analyzer_service import TemplateAnalyzerService
from app.services.template_content_service import TemplateContentService
from app.services.template_settings_service import TemplateSettingsService
from app.services.thumbnail_service import ThumbnailService
from app.schemas.template_metadata import TemplateAnalysisResult
from app.schemas.template_settings import (
    TemplateContentUpdate,
    TemplateContentResponse,
    TemplateSettingsUpdate,
    TemplateSettingsResponse
)
from app.config import get_mock_user
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _normalize_attachment_name(value: Any) -> Optional[str]:
    if value is None:
        return None
    name = str(value).strip()
    return name or None


def _looks_like_attachment_key(key: str) -> bool:
    lowered = key.lower()
    return "attachment" in lowered or "vedlegg" in lowered


def _extract_attachment_names_from_value(value: Any) -> list[str]:
    names: list[str] = []
    if value is None:
        return names
    if isinstance(value, list):
        for entry in value:
            names.extend(_extract_attachment_names_from_value(entry))
        return names
    if isinstance(value, dict):
        for key in ("name", "fileName", "filename", "title", "documentName", "attachmentName", "templateName"):
            if key in value:
                name = _normalize_attachment_name(value.get(key))
                if name:
                    names.append(name)
                    break
        return names
    name = _normalize_attachment_name(value)
    if name:
        names.append(name)
    return names


def _find_attachment_values(source: dict[str, Any], *, depth: int = 0, max_depth: int = 2) -> list[Any]:
    if depth > max_depth:
        return []
    values: list[Any] = []
    for key, value in source.items():
        if _looks_like_attachment_key(key):
            values.append(value)
        if isinstance(value, dict):
            values.extend(_find_attachment_values(value, depth=depth + 1, max_depth=max_depth))
    return values


def _extract_attachment_names(metadata_json: Optional[dict]) -> list[str]:
    if not isinstance(metadata_json, dict):
        return []

    # Prefer normalized attachments stored by importer
    if isinstance(metadata_json.get("vitec_attachments"), list):
        raw_entries = metadata_json.get("vitec_attachments", [])
        names = _extract_attachment_names_from_value(raw_entries)
        return sorted(set(names))

    candidates: list[Any] = []
    for key in ("attachments", "attachmentTemplates", "attachmentTemplateList"):
        if isinstance(metadata_json.get(key), list):
            candidates.append(metadata_json.get(key))

    for source_key in ("vitec_details", "vitec_raw"):
        source = metadata_json.get(source_key)
        if isinstance(source, dict):
            candidates.extend(_find_attachment_values(source))

    names: list[str] = []
    for candidate in candidates:
        names.extend(_extract_attachment_names_from_value(candidate))

    return sorted(set(names))


# Pydantic schemas for request bodies
class TemplateUpdateRequest(BaseModel):
    """Request body for updating a template."""
    title: Optional[str] = Field(None, max_length=255, description="Template title")
    description: Optional[str] = Field(None, max_length=2000, description="Template description")
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$", description="Template status")
    category_ids: Optional[List[UUID]] = Field(
        None, description="Category IDs to associate with the template"
    )


def get_current_user():
    """Get current user (mocked for Phase 1)."""
    return get_mock_user()


@router.get("")
async def list_templates(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    category_id: Optional[str] = Query(None, description="Filter by category UUID"),
    receiver: Optional[str] = Query(None, description="Filter by receiver (primary or extra)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
):
    """List all templates with filtering and pagination."""
    # Validate category_id is a valid UUID if provided
    validated_category_id: Optional[UUID] = None
    if category_id:
        try:
            validated_category_id = UUID(category_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category_id format: '{category_id}' is not a valid UUID"
            )
    
    templates, total = await TemplateService.get_list(
        db,
        status=status,
        search=search,
        category_id=validated_category_id,
        receiver=receiver,
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
                "attachments": _extract_attachment_names(t.metadata_json),
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
        "attachments": _extract_attachment_names(template.metadata_json),
    }


@router.post("", status_code=201)
async def create_template(
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("draft"),
    auto_sanitize: bool = Form(False),
    user: dict = Depends(get_current_user)
):
    """
    Upload a new template.
    
    Args:
        auto_sanitize: If True, HTML files will be sanitized for Vitec compatibility.
                       Defaults to False. Use the Sanitizer tool for manual cleanup.
    """
    # Validate file type
    allowed_types = ["docx", "doc", "pdf", "xlsx", "xls", "html", "htm"]
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Read file
    file_content = await file.read()
    file_size = len(file_content)
    
    # For HTML files, decode and optionally sanitize the content
    html_content = None
    if file_ext in ["html", "htm"]:
        try:
            html_content = file_content.decode("utf-8")
        except UnicodeDecodeError:
            html_content = file_content.decode("latin-1")
        
        # Sanitize HTML if requested
        if auto_sanitize:
            sanitizer = get_sanitizer_service()
            html_content = sanitizer.sanitize(html_content)
            logger.info(f"Sanitized HTML content for template: {title}")
    
    # Upload to Azure Blob Storage
    storage_service = get_azure_storage_service()
    blob_url = None
    
    if storage_service.is_configured:
        # Generate unique blob name with timestamp to avoid collisions
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_name = f"{timestamp}_{file.filename}"
        
        # Upload to Azure
        blob_url = await storage_service.upload_file(
            file_data=io.BytesIO(file_content),
            blob_name=blob_name,
            content_type=file.content_type
        )
        
        if blob_url:
            logger.info(f"Uploaded to Azure: {blob_url}")
        else:
            logger.warning(f"Azure upload failed for {file.filename}, using mock URL")
    
    # Fallback to mock URL if Azure not configured or upload failed
    if not blob_url:
        blob_url = f"mock://templates/{file.filename}"
        logger.info(f"Using mock URL: {blob_url}")
    
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
        status=status,
        content=html_content
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
    if body.category_ids is not None:
        updates["category_ids"] = body.category_ids
    
    template = await TemplateService.update(
        db,
        template,
        updated_by=user["email"],
        **updates
    )
    
    # Prepare log details (serialize non-JSON types)
    log_details = updates.copy()
    if "category_ids" in log_details and log_details["category_ids"]:
        log_details["category_ids"] = [str(uid) for uid in log_details["category_ids"]]
    if "published_at" in log_details and log_details["published_at"]:
        log_details["published_at"] = log_details["published_at"].isoformat()

    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template.id,
        action="updated",
        user_email=user["email"],
        details=log_details
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
    
    # Handle Vitec Next templates (internal content)
    if template.azure_blob_url and template.azure_blob_url.startswith("vitec-next://"):
        if template.content and template.file_type in ["html", "htm"]:
            import base64
            # Return content as Data URI
            content_bytes = template.content.encode("utf-8")
            b64_content = base64.b64encode(content_bytes).decode("ascii")
            return {
                "download_url": f"data:text/html;base64,{b64_content}",
                "file_name": template.file_name,
                "expires_at": None
            }
        elif not template.content:
             # If no content is found (should not happen for HTML based on check), fallback or error
             logger.warning(f"Vitec template {template.id} has no content in DB.")

    # TODO: Generate SAS URL for Azure Blob Storage
    return {
        "download_url": template.azure_blob_url,
        "file_name": template.file_name,
        "expires_at": datetime.now(timezone.utc).isoformat()
    }



@router.get("/{template_id}/content")
async def get_template_content(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the raw HTML content of a template.
    
    For HTML templates, returns the stored content directly.
    For other file types, returns an error (preview not supported).
    """
    template = await TemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if this is an HTML template
    if template.file_type not in ["html", "htm"]:
        raise HTTPException(
            status_code=400,
            detail=f"Preview not supported for file type: {template.file_type}. Only HTML templates can be previewed."
        )
    
    # Check if content exists
    if not template.content:
        raise HTTPException(
            status_code=404,
            detail="Template content not found. The template may need to be re-uploaded."
        )
    
    return {
        "id": str(template.id),
        "title": template.title,
        "file_type": template.file_type,
        "content": template.content
    }


@router.get("/{template_id}/analyze", response_model=TemplateAnalysisResult)
async def analyze_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a template for merge fields, conditions, and loops.
    
    Returns all Vitec-specific patterns found in the template HTML,
    along with a list of unknown fields not in the merge_fields registry.
    """
    result = await TemplateAnalyzerService.analyze(db, template_id)
    return TemplateAnalysisResult(**result)


@router.put("/{template_id}/content", response_model=TemplateContentResponse)
async def save_template_content(
    template_id: UUID,
    body: TemplateContentUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Save template HTML content.
    
    Creates a version snapshot before saving if content has changed.
    Re-scans for merge fields and updates the template.
    """
    result = await TemplateContentService.save_content(
        db,
        template_id,
        content=body.content,
        updated_by=user["email"],
        change_notes=body.change_notes,
        auto_sanitize=body.auto_sanitize
    )
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template_id,
        action="content_updated",
        user_email=user["email"],
        details={"version": result["version"]}
    )
    
    return TemplateContentResponse(**result)


@router.put("/{template_id}/settings", response_model=TemplateSettingsResponse)
async def update_template_settings(
    template_id: UUID,
    body: TemplateSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Update template Vitec metadata settings."""
    await TemplateSettingsService.update_settings(
        db,
        template_id,
        updated_by=user["email"],
        **body.model_dump(exclude_unset=True)
    )
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template_id,
        action="settings_updated",
        user_email=user["email"],
        details=body.model_dump(exclude_unset=True, mode="json")
    )
    
    settings = await TemplateSettingsService.get_settings(db, template_id)
    return TemplateSettingsResponse(**settings)


@router.get("/{template_id}/settings", response_model=TemplateSettingsResponse)
async def get_template_settings(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get template settings."""
    settings = await TemplateSettingsService.get_settings(db, template_id)
    return TemplateSettingsResponse(**settings)


@router.post("/{template_id}/thumbnail")
async def generate_thumbnail(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Generate a static thumbnail for a template.
    
    Requires Playwright to be installed. Returns 501 if not available.
    """
    if not ThumbnailService.is_available():
        raise HTTPException(
            status_code=501,
            detail="Thumbnail generation not available. Playwright is not installed."
        )
    
    result = await ThumbnailService.generate_thumbnail(db, template_id)
    
    # Audit log
    await AuditService.log(
        db,
        entity_type="template",
        entity_id=template_id,
        action="thumbnail_generated",
        user_email=user["email"]
    )
    
    return result

