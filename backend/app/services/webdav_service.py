"""
WebDAV Storage Service

Provides access to network storage via WebDAV protocol.
Supports browsing, downloading, uploading, and file management operations.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from webdav3.client import Client
from webdav3.exceptions import WebDavException

from app.config import settings

logger = logging.getLogger(__name__)

# Thread pool for running sync WebDAV operations
_executor = ThreadPoolExecutor(max_workers=4)


@dataclass
class StorageItem:
    """Represents a file or directory in the storage."""
    name: str
    path: str
    is_directory: bool
    size: int = 0
    modified: Optional[datetime] = None
    content_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "is_directory": self.is_directory,
            "size": self.size,
            "modified": self.modified.isoformat() if self.modified else None,
            "content_type": self.content_type,
        }


class WebDAVService:
    """
    Service for interacting with WebDAV network storage.
    
    All operations are wrapped to run in a thread pool since
    webdavclient3 is synchronous.
    """
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._configured = False
        self._initialize()
    
    def _initialize(self):
        """Initialize WebDAV client with settings."""
        if not settings.WEBDAV_URL:
            logger.warning("WebDAV URL not configured. Storage features disabled.")
            return
        
        if not settings.WEBDAV_USERNAME or not settings.WEBDAV_PASSWORD:
            logger.warning("WebDAV credentials not configured. Storage features disabled.")
            return
        
        try:
            options = {
                "webdav_hostname": settings.WEBDAV_URL,
                "webdav_login": settings.WEBDAV_USERNAME,
                "webdav_password": settings.WEBDAV_PASSWORD,
            }
            self._client = Client(options)
            self._configured = True
            logger.info(f"WebDAV client configured for: {settings.WEBDAV_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize WebDAV client: {e}")
            self._configured = False
    
    @property
    def is_configured(self) -> bool:
        """Check if WebDAV is properly configured."""
        return self._configured and self._client is not None
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, lambda: func(*args, **kwargs))
    
    async def check_connection(self) -> bool:
        """Test the WebDAV connection."""
        if not self.is_configured:
            return False
        
        try:
            await self._run_sync(self._client.check)
            return True
        except WebDavException as e:
            logger.error(f"WebDAV connection check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking WebDAV connection: {e}")
            return False
    
    async def list_directory(self, path: str = "/") -> List[StorageItem]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path (default: root)
            
        Returns:
            List of StorageItem objects
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        
        try:
            # Ensure path ends with / for directory listing
            if not path.endswith("/"):
                path = path + "/"
            
            # Get list of items - try with get_info first, fallback to simple list
            try:
                items = await self._run_sync(self._client.list, path, get_info=True)
            except Exception as e:
                logger.warning(f"get_info=True failed, trying simple list: {e}")
                items = await self._run_sync(self._client.list, path)
            
            logger.info(f"WebDAV list returned {len(items) if items else 0} items for path: {path}")
            logger.info(f"Raw items: {items}")
            
            result = []
            for item in items:
                # Skip the current directory entry
                if isinstance(item, dict):
                    name = item.get("name", "")
                    item_path = item.get("path", "")
                else:
                    # Sometimes returns just strings
                    name = str(item)
                    item_path = f"{path.rstrip('/')}/{item}"
                
                # Skip parent directory references and current directory
                if not name or name == "." or name == ".." or name == "/":
                    continue
                
                # Skip if the item path is the same as the requested path (current dir)
                clean_path = path.rstrip("/")
                clean_item_path = item_path.rstrip("/")
                if clean_item_path == clean_path or clean_item_path == "":
                    continue
                
                # Determine if directory (ends with /)
                is_dir = name.endswith("/") or item_path.endswith("/")
                name = name.rstrip("/")
                item_path = item_path.rstrip("/")
                
                # Get additional info if available
                size = 0
                modified = None
                content_type = None
                
                if isinstance(item, dict):
                    size = int(item.get("size", 0) or 0)
                    modified_str = item.get("modified")
                    if modified_str:
                        try:
                            modified = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            pass
                    content_type = item.get("content_type")
                
                result.append(StorageItem(
                    name=name,
                    path=item_path,
                    is_directory=is_dir,
                    size=size,
                    modified=modified,
                    content_type=content_type,
                ))
            
            # Sort: directories first, then by name
            result.sort(key=lambda x: (not x.is_directory, x.name.lower()))
            return result
            
        except WebDavException as e:
            logger.error(f"Failed to list directory {path}: {e}")
            raise RuntimeError(f"Failed to list directory: {e}")
    
    async def get_file_info(self, path: str) -> Optional[StorageItem]:
        """
        Get information about a file or directory.
        
        Args:
            path: Path to the item
            
        Returns:
            StorageItem or None if not found
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            info = await self._run_sync(self._client.info, path)
            
            if not info:
                return None
            
            name = path.rstrip("/").split("/")[-1]
            is_dir = info.get("isdir", False) or path.endswith("/")
            
            modified = None
            modified_str = info.get("modified")
            if modified_str:
                try:
                    modified = datetime.fromisoformat(modified_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
            
            return StorageItem(
                name=name,
                path=path,
                is_directory=is_dir,
                size=int(info.get("size", 0) or 0),
                modified=modified,
                content_type=info.get("content_type"),
            )
        except WebDavException as e:
            logger.error(f"Failed to get info for {path}: {e}")
            return None
    
    async def download_file(self, path: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            path: Path to the file
            
        Returns:
            File contents as bytes
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            # webdavclient3 requires downloading to a buffer or file
            import io
            buffer = io.BytesIO()
            
            def download():
                self._client.download_from(buffer, path)
                return buffer.getvalue()
            
            return await self._run_sync(download)
            
        except WebDavException as e:
            logger.error(f"Failed to download {path}: {e}")
            raise RuntimeError(f"Failed to download file: {e}")
    
    async def upload_file(self, path: str, content: bytes, content_type: str = None) -> bool:
        """
        Upload a file to storage.
        
        Args:
            path: Destination path
            content: File content as bytes
            content_type: Optional MIME type
            
        Returns:
            True if successful
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            import io
            buffer = io.BytesIO(content)
            
            await self._run_sync(self._client.upload_to, buffer, path)
            logger.info(f"Uploaded file to {path}")
            return True
            
        except WebDavException as e:
            logger.error(f"Failed to upload to {path}: {e}")
            raise RuntimeError(f"Failed to upload file: {e}")
    
    async def create_directory(self, path: str) -> bool:
        """
        Create a new directory.
        
        Args:
            path: Path for the new directory
            
        Returns:
            True if successful
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            await self._run_sync(self._client.mkdir, path)
            logger.info(f"Created directory: {path}")
            return True
            
        except WebDavException as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise RuntimeError(f"Failed to create directory: {e}")
    
    async def delete(self, path: str) -> bool:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            
        Returns:
            True if successful
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            await self._run_sync(self._client.clean, path)
            logger.info(f"Deleted: {path}")
            return True
            
        except WebDavException as e:
            logger.error(f"Failed to delete {path}: {e}")
            raise RuntimeError(f"Failed to delete: {e}")
    
    async def move(self, source: str, destination: str) -> bool:
        """
        Move or rename a file/directory.
        
        Args:
            source: Current path
            destination: New path
            
        Returns:
            True if successful
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            await self._run_sync(self._client.move, source, destination)
            logger.info(f"Moved {source} to {destination}")
            return True
            
        except WebDavException as e:
            logger.error(f"Failed to move {source} to {destination}: {e}")
            raise RuntimeError(f"Failed to move: {e}")
    
    async def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory.
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            True if successful
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            await self._run_sync(self._client.copy, source, destination)
            logger.info(f"Copied {source} to {destination}")
            return True
            
        except WebDavException as e:
            logger.error(f"Failed to copy {source} to {destination}: {e}")
            raise RuntimeError(f"Failed to copy: {e}")
    
    async def exists(self, path: str) -> bool:
        """
        Check if a path exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if exists
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")
        
        try:
            return await self._run_sync(self._client.check, path)
        except WebDavException:
            return False


# Singleton instance
_webdav_service: Optional[WebDAVService] = None


def get_webdav_service() -> WebDAVService:
    """Get the WebDAV service singleton."""
    global _webdav_service
    if _webdav_service is None:
        _webdav_service = WebDAVService()
    return _webdav_service
