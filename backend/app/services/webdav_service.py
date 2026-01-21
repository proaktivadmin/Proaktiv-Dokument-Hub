"""
WebDAV Storage Service

Provides access to network storage via WebDAV protocol.
Supports browsing, downloading, uploading, and file management operations.

Uses httpx with Digest authentication for servers that require it.

NOTE: WebDAV integration is currently disabled pending proper configuration
with the proaktiv.no server. The server requires specific URL/protocol settings.
"""

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
    modified: datetime | None = None
    content_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
        self._auth: httpx.DigestAuth | None = None
        self._initialize()

    def _initialize(self):
        """Initialize WebDAV client with settings."""
        if not settings.WEBDAV_URL:
            logger.info("WebDAV URL not configured. Storage features disabled.")
            return

        # Check for placeholder/disabled value
        if settings.WEBDAV_URL.lower() in ("disabled", "none", ""):
            logger.info("WebDAV explicitly disabled.")
            return

        if not settings.WEBDAV_USERNAME or not settings.WEBDAV_PASSWORD:
            logger.warning("WebDAV credentials not configured. Storage features disabled.")
            return

        try:
            self._base_url = settings.WEBDAV_URL.rstrip("/")
            self._auth = httpx.DigestAuth(settings.WEBDAV_USERNAME, settings.WEBDAV_PASSWORD)
            self._configured = True
            logger.info(f"WebDAV client configured for: {settings.WEBDAV_URL}")
        except Exception as e:
            logger.error(f"Failed to initialize WebDAV client: {e}")
            self._configured = False

    @property
    def is_configured(self) -> bool:
        """Check if WebDAV is properly configured."""
        return self._configured and self._auth is not None

    def _get_client(self) -> httpx.AsyncClient:
        """Get an async HTTP client with digest auth."""
        return httpx.AsyncClient(auth=self._auth, timeout=30.0, follow_redirects=False)

    def _parse_propfind_response(self, xml_text: str, base_path: str) -> list[StorageItem]:
        """Parse WebDAV PROPFIND XML response into StorageItem list."""
        items = []

        from urllib.parse import unquote, urlparse

        base_url_path = urlparse(self._base_url).path.rstrip("/")

        try:
            root = ET.fromstring(xml_text)
            ns = {"d": "DAV:"}

            for response in root.findall(".//d:response", ns):
                href_elem = response.find("d:href", ns)
                if href_elem is None:
                    continue

                href = href_elem.text or ""

                propstat = response.find("d:propstat", ns)
                if propstat is None:
                    continue

                prop = propstat.find("d:prop", ns)
                if prop is None:
                    continue

                # Check if directory
                resourcetype = prop.find("d:resourcetype", ns)
                is_dir = resourcetype is not None and resourcetype.find("d:collection", ns) is not None

                # Get display name or extract from href
                displayname = prop.find("d:displayname", ns)
                if displayname is not None and displayname.text:
                    name = displayname.text
                else:
                    name = unquote(href.rstrip("/").split("/")[-1])

                if not name:
                    continue

                # Get size
                size = 0
                content_length = prop.find("d:getcontentlength", ns)
                if content_length is not None and content_length.text:
                    try:
                        size = int(content_length.text)
                    except ValueError:
                        pass

                # Get modified date
                modified = None
                lastmodified = prop.find("d:getlastmodified", ns)
                if lastmodified is not None and lastmodified.text:
                    try:
                        from email.utils import parsedate_to_datetime

                        modified = parsedate_to_datetime(lastmodified.text)
                    except Exception:
                        pass

                # Get content type
                content_type = None
                contenttype = prop.find("d:getcontenttype", ns)
                if contenttype is not None:
                    content_type = contenttype.text

                # Build path
                parsed_href = urlparse(href)
                full_path = unquote(parsed_href.path) if parsed_href.path else href

                if base_url_path and full_path.startswith(base_url_path):
                    item_path = full_path[len(base_url_path) :]
                else:
                    item_path = full_path

                if not item_path.startswith("/"):
                    item_path = "/" + item_path

                # Skip the current directory itself
                clean_base = base_path.rstrip("/")
                clean_item = item_path.rstrip("/")
                if clean_item == clean_base or clean_item == "":
                    continue

                items.append(
                    StorageItem(
                        name=name,
                        path=item_path,
                        is_directory=is_dir,
                        size=size,
                        modified=modified,
                        content_type=content_type,
                    )
                )

        except ET.ParseError as e:
            logger.error(f"Failed to parse PROPFIND response: {e}")

        items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
        return items

    async def check_connection(self) -> bool:
        """Test the WebDAV connection."""
        if not self.is_configured:
            return False

        try:
            async with self._get_client() as client:
                response = await client.request(
                    "PROPFIND",
                    f"{self._base_url}/",
                    headers={"Depth": "0"},
                )
                return response.status_code in (200, 207)
        except Exception as e:
            logger.error(f"WebDAV connection check failed: {e}")
            return False

    async def list_directory(self, path: str = "/") -> list[StorageItem]:
        """
        List contents of a directory.

        Args:
            path: Directory path (default: root)

        Returns:
            List of StorageItem objects
        """
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        if not path.startswith("/"):
            path = "/" + path

        clean_path = path.rstrip("/") if path != "/" else "/"

        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{clean_path}/"

                response = await client.request(
                    "PROPFIND",
                    url,
                    headers={"Depth": "1"},
                )

                if response.status_code not in (200, 207):
                    logger.error(f"PROPFIND failed: {response.status_code}")
                    raise RuntimeError(f"Failed to list directory: HTTP {response.status_code}")

                items = self._parse_propfind_response(response.text, clean_path + "/")
                return items

        except httpx.HTTPError as e:
            logger.error(f"Failed to list directory {path}: {e}")
            raise RuntimeError(f"Failed to list directory: {e}")

    async def get_file_info(self, path: str) -> StorageItem | None:
        """Get information about a file or directory."""
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
        """Download a file from storage."""
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

    async def upload_file(self, path: str, content: bytes, content_type: str | None = None) -> bool:
        """Upload a file to storage."""
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                headers = {"Content-Type": content_type} if content_type else {}

                response = await client.put(url, content=content, headers=headers)

                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"Upload failed: HTTP {response.status_code}")

                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to upload to {path}: {e}")
            raise RuntimeError(f"Failed to upload file: {e}")

    async def create_directory(self, path: str) -> bool:
        """Create a new directory."""
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.request("MKCOL", url)

                if response.status_code not in (200, 201):
                    raise RuntimeError(f"MKCOL failed: HTTP {response.status_code}")

                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to create directory {path}: {e}")
            raise RuntimeError(f"Failed to create directory: {e}")

    async def delete(self, path: str) -> bool:
        """Delete a file or directory."""
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.delete(url)

                if response.status_code not in (200, 204):
                    raise RuntimeError(f"DELETE failed: HTTP {response.status_code}")

                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to delete {path}: {e}")
            raise RuntimeError(f"Failed to delete: {e}")

    async def move(self, source: str, destination: str) -> bool:
        """Move or rename a file/directory."""
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        try:
            async with self._get_client() as client:
                src_url = f"{self._base_url}{source}"
                dest_url = f"{self._base_url}{destination}"

                response = await client.request("MOVE", src_url, headers={"Destination": dest_url})

                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"MOVE failed: HTTP {response.status_code}")

                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to move {source} to {destination}: {e}")
            raise RuntimeError(f"Failed to move: {e}")

    async def copy(self, source: str, destination: str) -> bool:
        """Copy a file or directory."""
        if not self.is_configured:
            raise RuntimeError("WebDAV not configured")

        try:
            async with self._get_client() as client:
                src_url = f"{self._base_url}{source}"
                dest_url = f"{self._base_url}{destination}"

                response = await client.request("COPY", src_url, headers={"Destination": dest_url})

                if response.status_code not in (200, 201, 204):
                    raise RuntimeError(f"COPY failed: HTTP {response.status_code}")

                return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to copy {source} to {destination}: {e}")
            raise RuntimeError(f"Failed to copy: {e}")

    async def exists(self, path: str) -> bool:
        """Check if a path exists."""
        if not self.is_configured:
            return False

        try:
            async with self._get_client() as client:
                url = f"{self._base_url}{path}"
                response = await client.request("PROPFIND", url, headers={"Depth": "0"})
                return response.status_code in (200, 207)
        except Exception:
            return False


# Singleton instance
_webdav_service: WebDAVService | None = None


def get_webdav_service() -> WebDAVService:
    """Get the WebDAV service singleton."""
    global _webdav_service
    if _webdav_service is None:
        _webdav_service = WebDAVService()
    return _webdav_service
