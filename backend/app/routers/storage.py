"""
Storage Router

API endpoints for WebDAV network storage operations.
Provides file browsing, management, and import-to-library functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
import logging
import io

from app.database import get_db
from app.config import get_mock_user
from app.services.webdav_service import get_webdav_service, StorageItem
from app.services.template_service import TemplateService
from app.services.sanitizer_service import get_sanitizer_service
from app.services.audit_service import AuditService


def get_current_user():
    """Get current user (mocked for Phase 1)."""
    return get_mock_user()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/storage", tags=["Storage"])


# Request/Response Models

class StorageItemResponse(BaseModel):
    """Response model for a storage item."""
    name: str
    path: str
    is_directory: bool
    size: int = 0
    modified: Optional[str] = None
    content_type: Optional[str] = None


class BrowseResponse(BaseModel):
    """Response for browse endpoint."""
    path: str
    items: List[StorageItemResponse]
    parent_path: Optional[str] = None


class MoveRequest(BaseModel):
    """Request to move/rename a file."""
    source: str
    destination: str


class ImportRequest(BaseModel):
    """Request to import a file to the template library."""
    path: str
    title: str
    description: Optional[str] = None
    status: str = "draft"
    category_id: Optional[str] = None
    auto_sanitize: bool = False


class StatusResponse(BaseModel):
    """Response for status/health checks."""
    configured: bool
    connected: bool
    message: str


# Helper Functions

def _item_to_response(item: StorageItem) -> StorageItemResponse:
    """Convert StorageItem to response model."""
    return StorageItemResponse(
        name=item.name,
        path=item.path,
        is_directory=item.is_directory,
        size=item.size,
        modified=item.modified.isoformat() if item.modified else None,
        content_type=item.content_type,
    )


def _get_parent_path(path: str) -> Optional[str]:
    """Get parent directory path."""
    if not path or path == "/" or path == "":
        return None
    
    # Remove trailing slash and get parent
    clean_path = path.rstrip("/")
    parts = clean_path.split("/")
    
    if len(parts) <= 1:
        return "/"
    
    return "/".join(parts[:-1]) or "/"


# Endpoints

@router.get("/status", response_model=StatusResponse)
async def get_storage_status():
    """
    Check WebDAV storage connection status.
    
    Returns configuration and connection status.
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        return StatusResponse(
            configured=False,
            connected=False,
            message="WebDAV not configured. Set WEBDAV_URL, WEBDAV_USERNAME, and WEBDAV_PASSWORD."
        )
    
    try:
        connected = await service.check_connection()
        return StatusResponse(
            configured=True,
            connected=connected,
            message="Connected to WebDAV storage" if connected else "Failed to connect to WebDAV storage"
        )
    except Exception as e:
        logger.error(f"Error checking storage status: {e}")
        return StatusResponse(
            configured=True,
            connected=False,
            message=f"Connection error: {str(e)}"
        )


@router.get("/debug")
async def debug_storage(
    path: str = Query("/", description="Directory path to test"),
    user: dict = Depends(get_current_user)
):
    """
    Debug endpoint to see raw WebDAV response.
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        return {"error": "WebDAV not configured"}
    
    try:
        from app.config import settings
        import httpx
        import base64
        
        results = {}
        
        # Test webdavclient3 methods
        try:
            exists_shared = await service._run_sync(service._client.check, "Shared files/")
            results["check_shared_files"] = exists_shared
        except Exception as e:
            results["check_shared_files"] = {"error": str(e)}
        
        try:
            exists_files = await service._run_sync(service._client.check, "Files/")
            results["check_files"] = exists_files
        except Exception as e:
            results["check_files"] = {"error": str(e)}
        
        # Try raw PROPFIND request
        try:
            auth_string = f"{settings.WEBDAV_USERNAME}:{settings.WEBDAV_PASSWORD}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {auth_bytes}",
                "Depth": "1",
                "Content-Type": "application/xml",
            }
            
            propfind_body = """<?xml version="1.0" encoding="utf-8"?>
<propfind xmlns="DAV:">
  <prop>
    <resourcetype/>
    <getcontentlength/>
    <getlastmodified/>
  </prop>
</propfind>"""
            
            url = settings.WEBDAV_URL.rstrip("/") + "/"
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.request(
                    "PROPFIND",
                    url,
                    headers=headers,
                    content=propfind_body
                )
                
                # Also try without trailing slash
                url_no_slash = settings.WEBDAV_URL.rstrip("/")
                response2 = await client.request(
                    "PROPFIND",
                    url_no_slash,
                    headers=headers,
                    content=propfind_body
                )
                
                results["propfind_status"] = response.status_code
                results["propfind_headers"] = dict(response.headers)
                # Truncate body if too long
                body = response.text
                results["propfind_body"] = body[:3000] if len(body) > 3000 else body
                results["propfind_body_length"] = len(body)
                
                # Second request without trailing slash
                results["propfind2_url"] = url_no_slash
                results["propfind2_status"] = response2.status_code
                body2 = response2.text
                results["propfind2_body"] = body2[:3000] if len(body2) > 3000 else body2
                results["propfind2_body_length"] = len(body2)
                
        except Exception as e:
            results["propfind_error"] = str(e)
        
        return {
            "webdav_url": settings.WEBDAV_URL,
            "original_path": path,
            "results": results,
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@router.get("/browse", response_model=BrowseResponse)
async def browse_storage(
    path: str = Query("/", description="Directory path to browse"),
    user: dict = Depends(get_current_user)
):
    """
    List contents of a directory in the storage.
    
    Args:
        path: Directory path (default: root)
        
    Returns:
        List of files and directories
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        items = await service.list_directory(path)
        
        return BrowseResponse(
            path=path,
            items=[_item_to_response(item) for item in items],
            parent_path=_get_parent_path(path)
        )
    except RuntimeError as e:
        error_msg = str(e)
        # Check for common error patterns
        if "401" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="WebDAV authentication failed. Check WEBDAV_USERNAME and WEBDAV_PASSWORD."
            )
        elif "404" in error_msg:
            raise HTTPException(
                status_code=404,
                detail=f"Directory not found: {path}"
            )
        elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to WebDAV server. Check WEBDAV_URL."
            )
        else:
            raise HTTPException(status_code=500, detail=error_msg)


@router.get("/download")
async def download_file(
    path: str = Query(..., description="File path to download"),
    user: dict = Depends(get_current_user)
):
    """
    Download a file from storage.
    
    Args:
        path: Path to the file
        
    Returns:
        File content as streaming response
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        # Get file info for content type
        info = await service.get_file_info(path)
        if not info:
            raise HTTPException(status_code=404, detail="File not found")
        
        if info.is_directory:
            raise HTTPException(status_code=400, detail="Cannot download a directory")
        
        # Download content
        content = await service.download_file(path)
        
        # Determine content type
        content_type = info.content_type or "application/octet-stream"
        filename = info.name
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(content)),
            }
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_file(
    path: str = Form(..., description="Destination directory path"),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a file to storage.
    
    Args:
        path: Destination directory
        file: File to upload
        
    Returns:
        Upload result with new file path
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Build destination path
        dest_path = f"{path.rstrip('/')}/{file.filename}"
        
        # Upload
        await service.upload_file(dest_path, content, file.content_type)
        
        logger.info(f"User {user['email']} uploaded file to {dest_path}")
        
        return {
            "success": True,
            "path": dest_path,
            "filename": file.filename,
            "size": len(content)
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mkdir")
async def create_directory(
    path: str = Form(..., description="Directory path to create"),
    user: dict = Depends(get_current_user)
):
    """
    Create a new directory in storage.
    
    Args:
        path: Path for the new directory
        
    Returns:
        Success status
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        await service.create_directory(path)
        logger.info(f"User {user['email']} created directory: {path}")
        
        return {"success": True, "path": path}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/move")
async def move_file(
    request: MoveRequest,
    user: dict = Depends(get_current_user)
):
    """
    Move or rename a file/directory.
    
    Args:
        source: Current path
        destination: New path
        
    Returns:
        Success status
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        await service.move(request.source, request.destination)
        logger.info(f"User {user['email']} moved {request.source} to {request.destination}")
        
        return {
            "success": True,
            "source": request.source,
            "destination": request.destination
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_file(
    path: str = Query(..., description="Path to delete"),
    user: dict = Depends(get_current_user)
):
    """
    Delete a file or directory from storage.
    
    Args:
        path: Path to delete
        
    Returns:
        Success status
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        await service.delete(path)
        logger.info(f"User {user['email']} deleted: {path}")
        
        return {"success": True, "path": path}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import-to-library")
async def import_to_library(
    request: ImportRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """
    Import a file from storage into the template library.
    
    Downloads the file from WebDAV and creates a new template record.
    
    Args:
        path: Path to the file in storage
        title: Template title
        description: Optional description
        status: Template status (draft/published)
        category_id: Optional category ID
        auto_sanitize: Whether to sanitize HTML files
        
    Returns:
        Created template info
    """
    service = get_webdav_service()
    
    if not service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="WebDAV storage not configured"
        )
    
    try:
        # Get file info
        info = await service.get_file_info(request.path)
        if not info:
            raise HTTPException(status_code=404, detail="File not found")
        
        if info.is_directory:
            raise HTTPException(status_code=400, detail="Cannot import a directory")
        
        # Check file extension
        file_ext = info.name.split(".")[-1].lower() if "." in info.name else ""
        allowed_types = ["docx", "doc", "pdf", "xlsx", "xls", "html", "htm"]
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Download file content
        content = await service.download_file(request.path)
        
        # For HTML files, decode and optionally sanitize
        html_content = None
        if file_ext in ["html", "htm"]:
            try:
                html_content = content.decode("utf-8")
            except UnicodeDecodeError:
                html_content = content.decode("latin-1")
            
            if request.auto_sanitize:
                sanitizer = get_sanitizer_service()
                html_content = sanitizer.sanitize(html_content)
                logger.info(f"Sanitized HTML content for import: {request.title}")
        
        # Create template record
        # Use a mock URL since we're importing from WebDAV
        blob_url = f"webdav://{request.path}"
        
        # Parse category_ids
        category_ids = None
        if request.category_id:
            from uuid import UUID
            try:
                category_ids = [UUID(request.category_id)]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid category ID")
        
        template = await TemplateService.create(
            db,
            title=request.title,
            description=request.description,
            file_name=info.name,
            file_type=file_ext,
            file_size_bytes=info.size,
            azure_blob_url=blob_url,
            created_by=user["email"],
            status=request.status,
            category_ids=category_ids,
            content=html_content
        )
        
        # Audit log
        await AuditService.log(
            db,
            entity_type="template",
            entity_id=template.id,
            action="imported_from_storage",
            user_email=user["email"],
            details={
                "title": request.title,
                "source_path": request.path,
                "file_name": info.name
            }
        )
        
        await db.commit()
        
        logger.info(f"User {user['email']} imported {request.path} as template: {template.id}")
        
        return {
            "success": True,
            "template": {
                "id": str(template.id),
                "title": template.title,
                "file_name": template.file_name,
                "file_type": template.file_type,
                "status": template.status,
            }
        }
        
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
