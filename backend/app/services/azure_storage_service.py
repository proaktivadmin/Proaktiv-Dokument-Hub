"""
Azure Blob Storage Service

Handles file uploads, downloads, and management in Azure Blob Storage.
"""

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError, ResourceNotFoundError
from typing import Optional, BinaryIO, List, Dict, Any
from datetime import datetime, timedelta
import logging
import mimetypes

from app.config import settings

logger = logging.getLogger(__name__)


class AzureStorageService:
    """
    Service for interacting with Azure Blob Storage.
    
    Handles:
    - File uploads to blob storage
    - File downloads
    - Generating SAS URLs for secure access
    - Container management
    """
    
    def __init__(self):
        """Initialize the Azure Storage service."""
        self._client: Optional[BlobServiceClient] = None
        self._initialized = False
        self._connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self._container_name = settings.AZURE_STORAGE_CONTAINER_NAME
    
    @property
    def client(self) -> Optional[BlobServiceClient]:
        """Get or create the blob service client."""
        if not self._initialized:
            self._initialize()
        return self._client
    
    def _initialize(self) -> None:
        """Initialize the blob service client."""
        if not self._connection_string:
            logger.warning("Azure Storage connection string not configured")
            self._initialized = True
            return
        
        try:
            self._client = BlobServiceClient.from_connection_string(
                self._connection_string
            )
            self._initialized = True
            logger.info("Azure Blob Storage client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage client: {e}")
            self._initialized = True
            self._client = None
    
    @property
    def is_configured(self) -> bool:
        """Check if Azure Storage is properly configured."""
        return bool(self._connection_string) and self.client is not None
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Azure Blob Storage.
        
        Returns:
            Dict with connection status and details
        """
        result = {
            "connected": False,
            "configured": bool(self._connection_string),
            "container_name": self._container_name,
            "account_name": None,
            "containers": [],
            "error": None
        }
        
        if not self._connection_string:
            result["error"] = "AZURE_STORAGE_CONNECTION_STRING not configured"
            return result
        
        try:
            if self.client is None:
                result["error"] = "Failed to create blob service client"
                return result
            
            # Get account info
            account_info = self.client.get_account_information()
            result["account_name"] = self.client.account_name
            result["sku_name"] = account_info.get("sku_name", "unknown")
            result["account_kind"] = account_info.get("account_kind", "unknown")
            
            # List containers
            containers = []
            for container in self.client.list_containers():
                containers.append({
                    "name": container["name"],
                    "last_modified": container.get("last_modified", "").isoformat() if container.get("last_modified") else None
                })
            result["containers"] = containers
            
            # Check if our target container exists
            result["target_container_exists"] = any(
                c["name"] == self._container_name for c in containers
            )
            
            result["connected"] = True
            logger.info(f"Azure Storage connection test successful: {result['account_name']}")
            
        except AzureError as e:
            result["error"] = f"Azure error: {str(e)}"
            logger.error(f"Azure Storage connection test failed: {e}")
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"Azure Storage connection test failed unexpectedly: {e}")
        
        return result
    
    async def ensure_container_exists(self, container_name: Optional[str] = None) -> bool:
        """
        Ensure the container exists, create if it doesn't.
        
        Args:
            container_name: Container name (uses default if not provided)
            
        Returns:
            True if container exists or was created
        """
        if not self.is_configured:
            logger.warning("Azure Storage not configured, cannot create container")
            return False
        
        container = container_name or self._container_name
        
        try:
            container_client = self.client.get_container_client(container)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {container}")
            return True
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {e}")
            return False
    
    async def upload_file(
        self,
        file_data: BinaryIO,
        blob_name: str,
        container_name: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Upload a file to blob storage.
        
        Args:
            file_data: File data as binary stream
            blob_name: Name for the blob (can include path)
            container_name: Container name (uses default if not provided)
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the blob
            
        Returns:
            Blob URL if successful, None otherwise
        """
        if not self.is_configured:
            logger.warning("Azure Storage not configured, cannot upload file")
            return None
        
        container = container_name or self._container_name
        
        try:
            # Ensure container exists
            await self.ensure_container_exists(container)
            
            # Get blob client
            blob_client = self.client.get_blob_client(
                container=container,
                blob=blob_name
            )
            
            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(blob_name)
                content_type = content_type or "application/octet-stream"
            
            # Upload the file
            blob_client.upload_blob(
                file_data,
                overwrite=True,
                content_settings={"content_type": content_type},
                metadata=metadata
            )
            
            logger.info(f"Uploaded blob: {container}/{blob_name}")
            return blob_client.url
            
        except Exception as e:
            logger.error(f"Failed to upload file to blob storage: {e}")
            return None
    
    async def download_file(
        self,
        blob_name: str,
        container_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Download a file from blob storage.
        
        Args:
            blob_name: Name of the blob
            container_name: Container name (uses default if not provided)
            
        Returns:
            File contents as bytes, or None if not found
        """
        if not self.is_configured:
            logger.warning("Azure Storage not configured, cannot download file")
            return None
        
        container = container_name or self._container_name
        
        try:
            blob_client = self.client.get_blob_client(
                container=container,
                blob=blob_name
            )
            
            download_stream = blob_client.download_blob()
            return download_stream.readall()
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found: {container}/{blob_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to download file from blob storage: {e}")
            return None
    
    async def delete_file(
        self,
        blob_name: str,
        container_name: Optional[str] = None
    ) -> bool:
        """
        Delete a file from blob storage.
        
        Args:
            blob_name: Name of the blob
            container_name: Container name (uses default if not provided)
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.is_configured:
            logger.warning("Azure Storage not configured, cannot delete file")
            return False
        
        container = container_name or self._container_name
        
        try:
            blob_client = self.client.get_blob_client(
                container=container,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {container}/{blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {container}/{blob_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete file from blob storage: {e}")
            return False
    
    async def list_blobs(
        self,
        container_name: Optional[str] = None,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List blobs in a container.
        
        Args:
            container_name: Container name (uses default if not provided)
            prefix: Optional prefix to filter blobs
            
        Returns:
            List of blob info dictionaries
        """
        if not self.is_configured:
            logger.warning("Azure Storage not configured, cannot list blobs")
            return []
        
        container = container_name or self._container_name
        
        try:
            container_client = self.client.get_container_client(container)
            
            blobs = []
            for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "metadata": blob.metadata
                })
            
            return blobs
            
        except Exception as e:
            logger.error(f"Failed to list blobs: {e}")
            return []


# Singleton instance
_storage_service: Optional[AzureStorageService] = None


def get_azure_storage_service() -> AzureStorageService:
    """
    Get the singleton Azure Storage service instance.
    
    Returns:
        AzureStorageService instance
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = AzureStorageService()
    return _storage_service

