"""
WebDAV Storage Service

Provides access to network storage via WebDAV protocol.
Supports browsing, downloading, uploading, and file management operations.

Uses httpx with Digest authentication for servers that require it.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import xml.etree.ElementTree as ET

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

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
    
    Uses httpx with Digest authentication for compatibility with
    servers that require it (like IIS-based WebDAV).
    """
    
    def __init__(self):
        self._configured = False
        self._base_url = ""
        self._auth: Optional[httpx.DigestAuth] = None
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
            self._base_url = settings.WEBDAV_URL.rstrip("/")
            self._auth = httpx.DigestAuth(settings.WEBDAV_USERNAME, settings.WEBDAV_PASSWORD)
            self._configured = True
            logger.info(f"WebDAV client configured for: {settings.WEBDAV_URL} (Digest auth)")
        except Exception as e:
            logger.error(f"Failed to initialize WebDAV client: {e}")
            self._configured = False
    
    @property
    def is_configured(self) -> bool:
        """Check if WebDAV is properly configured."""
        return self._configured and self._auth is not None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get an async HTTP client with digest auth."""
        # Don't follow redirects - WebDAV servers may redirect in ways that break PROPFIND
        return httpx.AsyncClient(
            auth=self._auth,
            timeout=30.0,
            follow_redirects=False
        )
    
    def _parse_propfind_response(self, xml_text: str, base_path: str) -> List[StorageItem]:
        """Parse WebDAV PROPFIND XML response into StorageItem list."""
        items = []
        
        # Extract the path prefix from base_url (e.g., "/d" from "https://proaktiv.no/d")
        from urllib.parse import urlparse
        base_url_path = urlparse(self._base_url).path.rstrip('/')
        
        # #region agent log
        logger.info(f"[DEBUG-H1] Parsing PROPFIND: base_path={base_path}, base_url_path={base_url_path}, xml_len={len(xml_text)}")
        logger.info(f"[DEBUG-H1] XML preview: {xml_text[:300]}")
        # #endregion
        
        try:
            # Parse XML
            root = ET.fromstring(xml_text)
            
            # WebDAV namespace
            ns = {
                'd': 'DAV:',
            }
            
            # Find all response elements
            for response in root.findall('.//d:response', ns):
                href_elem = response.find('d:href', ns)
                if href_elem is None:
                    continue
                
                href = href_elem.text or ""
                
                # Get properties
                propstat = response.find('d:propstat', ns)
                if propstat is None:
                    continue
                
                prop = propstat.find('d:prop', ns)
                if prop is None:
                    continue
                
                # Check if directory
                resourcetype = prop.find('d:resourcetype', ns)
                is_dir = resourcetype is not None and resourcetype.find('d:collection', ns) is not None
                
                # Get display name or extract from href
                displayname = prop.find('d:displayname', ns)
                if displayname is not None and displayname.text:
                    name = displayname.text
                else:
                    # Extract name from href
                    name = href.rstrip('/').split('/')[-1]
                    # URL decode
                    from urllib.parse import unquote
                    name = unquote(name)
                
                # Skip if no name or it's the current directory
                if not name:
                    continue
                
                # Get size
                size = 0
                content_length = prop.find('d:getcontentlength', ns)
                if content_length is not None and content_length.text:
                    try:
                        size = int(content_length.text)
                    except ValueError:
                        pass
                
                # Get modified date
                modified = None
                lastmodified = prop.find('d:getlastmodified', ns)
                if lastmodified is not None and lastmodified.text:
                    try:
                        from email.utils import parsedate_to_datetime
                        modified = parsedate_to_datetime(lastmodified.text)
                    except Exception:
                        pass
                
                # Get content type
                content_type = None
                contenttype = prop.find('d:getcontenttype', ns)
                if contenttype is not None:
                    content_type = contenttype.text
                
                # Build path - remove the base URL path prefix (e.g., /d) from href
                from urllib.parse import unquote
                parsed_href = urlparse(href)
                full_path = unquote(parsed_href.path) if parsed_href.path else href
                
                # Remove the base URL path prefix to get the relative path
                if base_url_path and full_path.startswith(base_url_path):
                    item_path = full_path[len(base_url_path):]
                else:
                    item_path = full_path
                
                # Ensure path starts with /
                if not item_path.startswith('/'):
                    item_path = '/' + item_path
                
                # Skip the current directory itself
                clean_base = base_path.rstrip('/')
                clean_item = item_path.rstrip('/')
                if clean_item == clean_base or clean_item == '':
                    continue
                
                # #region agent log
                if len(items) < 5:  # Only log first 5 items to avoid log spam
                    logger.info(f"[DEBUG-H3] Item: name={name}, href={href}, full_path={full_path}, item_path={item_path}, is_dir={is_dir}")
                # #endregion
                
                items.append(StorageItem(
                    name=name,
                    path=item_path,
                    is_directory=is_dir,
                    size=size,
                    modified=modified,
                    content_type=content_type,
                ))
                
        except ET.ParseError as e:
            logger.error(f"Failed to parse PROPFIND response: {e}")
        
        # Sort: directories first, then by name
        items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
        
        # #region agent log
        dirs = [i.name for i in items if i.is_directory][:5]
        files = [i.name for i in items if not i.is_directory][:5]
        logger.info(f"[DEBUG-H1] Parse complete: total={len(items)}, dirs={dirs}, files={files}, base_path={base_path}")
        # #endregion
        
        return items
    
    async def check_connection(self) -> bool:
        """Test the WebDAV connection."""
        if not self.is_configured:
            return False
        
        try:
            async with self._get_client() as client:
                # Try a simple PROPFIND on root
                response = await client.request(
                    "PROPFIND",
                    f"{self._base_url}/",
                    headers={"Depth": "0"},
                )
                return response.status_code in (200, 207)
        except Exception as e:
            logger.error(f"WebDAV connection check failed: {e}")
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
        
        # Ensure path ends with / for directory listing
        if not path.endswith("/"):
            path = path + "/"
        
        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                logger.info(f"PROPFIND request to: {url}")
                
                # #region agent log
                logger.info(f"[DEBUG-H2] PROPFIND: base_url={self._base_url}, path_arg={path}, full_url={url}")
                # #endregion
                
                response = await client.request(
                    "PROPFIND",
                    url,
                    headers={"Depth": "1"},
                )
                
                logger.info(f"PROPFIND response status: {response.status_code}")
                
                # Handle redirect - log the location for debugging
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("Location", "unknown")
                    logger.warning(f"PROPFIND got redirect to: {location}")
                    
                    # #region agent log
                    logger.info(f"[DEBUG-H2] Redirect: original={url}, location={location}, status={response.status_code}")
                    # #endregion
                    # Try following the redirect manually with PROPFIND
                    if location and location.startswith(("http://", "https://")):
                        logger.info(f"Following redirect with PROPFIND to: {location}")
                        response = await client.request(
                            "PROPFIND",
                            location if location.endswith('/') else location + '/',
                            headers={"Depth": "1"},
                        )
                        logger.info(f"Redirect PROPFIND response status: {response.status_code}")
                
                if response.status_code not in (200, 207):
                    logger.error(f"PROPFIND failed with status {response.status_code}: {response.text[:500]}")
                    raise RuntimeError(f"Failed to list directory: HTTP {response.status_code}")
                
                # Parse the XML response
                items = self._parse_propfind_response(response.text, path)
                logger.info(f"Parsed {len(items)} items from PROPFIND response")
                
                return items
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.request(
                    "PROPFIND",
                    url,
                    headers={"Depth": "0"},
                )
                
                if response.status_code not in (200, 207):
                    return None
                
                items = self._parse_propfind_response(response.text, path)
                return items[0] if items else None
                
        except Exception as e:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.get(url)
                
                if response.status_code != 200:
                    raise RuntimeError(f"Download failed: HTTP {response.status_code}")
                
                return response.content
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to download {path}: {e}")
            raise RuntimeError(f"Failed to download file: {e}")
    
    async def upload_file(self, path: str, content: bytes, content_type: Optional[str] = None) -> bool:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                headers = {}
                if content_type:
                    headers["Content-Type"] = content_type
                
                response = await client.put(url, content=content, headers=headers)
                
                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"Upload failed: HTTP {response.status_code}")
                
                logger.info(f"Uploaded file to {path}")
                return True
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.request("MKCOL", url)
                
                if response.status_code not in (200, 201):
                    raise RuntimeError(f"MKCOL failed: HTTP {response.status_code}")
                
                logger.info(f"Created directory: {path}")
                return True
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.delete(url)
                
                if response.status_code not in (200, 204):
                    raise RuntimeError(f"DELETE failed: HTTP {response.status_code}")
                
                logger.info(f"Deleted: {path}")
                return True
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                src_url = f"{self._base_url}{source}"
                dest_url = f"{self._base_url}{destination}"
                
                response = await client.request(
                    "MOVE",
                    src_url,
                    headers={"Destination": dest_url}
                )
                
                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"MOVE failed: HTTP {response.status_code}")
                
                logger.info(f"Moved {source} to {destination}")
                return True
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                src_url = f"{self._base_url}{source}"
                dest_url = f"{self._base_url}{destination}"
                
                response = await client.request(
                    "COPY",
                    src_url,
                    headers={"Destination": dest_url}
                )
                
                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"COPY failed: HTTP {response.status_code}")
                
                logger.info(f"Copied {source} to {destination}")
                return True
                
        except httpx.HTTPError as e:
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
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.request(
                    "PROPFIND",
                    url,
                    headers={"Depth": "0"}
                )
                return response.status_code in (200, 207)
        except Exception:
            return False


# Singleton instance
_webdav_service: Optional[WebDAVService] = None


def get_webdav_service() -> WebDAVService:
    """Get the WebDAV service singleton."""
    global _webdav_service
    if _webdav_service is None:
        _webdav_service = WebDAVService()
    return _webdav_service
