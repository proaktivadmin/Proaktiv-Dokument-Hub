"""
Azure Storage Service (DEPRECATED)

This service is deprecated as of V2.8 - template content is now stored in the database.
Kept for backward compatibility with existing code references.
"""

import logging
from typing import BinaryIO

logger = logging.getLogger(__name__)


class AzureStorageService:
    """
    Deprecated Azure Blob Storage service.

    Template content is now stored directly in the PostgreSQL database.
    This class provides stub methods to maintain API compatibility.
    """

    def __init__(self):
        self._configured = False
        logger.info("AzureStorageService initialized (deprecated - using database storage)")

    @property
    def is_configured(self) -> bool:
        """Check if Azure Storage is configured. Always returns False."""
        return False

    async def upload_file(self, file_data: BinaryIO, blob_name: str, content_type: str | None = None) -> str | None:
        """
        Upload file to Azure Blob Storage (deprecated).

        Returns None as Azure storage is no longer used.
        """
        logger.debug(f"Azure upload skipped (deprecated): {blob_name}")
        return None

    async def download_file(self, blob_name: str) -> bytes | None:
        """
        Download file from Azure Blob Storage (deprecated).

        Returns None as Azure storage is no longer used.
        """
        logger.debug(f"Azure download skipped (deprecated): {blob_name}")
        return None

    async def delete_file(self, blob_name: str) -> bool:
        """
        Delete file from Azure Blob Storage (deprecated).

        Returns True (no-op).
        """
        logger.debug(f"Azure delete skipped (deprecated): {blob_name}")
        return True

    async def check_connection(self) -> bool:
        """
        Check Azure connection (deprecated).

        Returns False as Azure is not configured.
        """
        return False


# Singleton instance
_azure_service: AzureStorageService | None = None


def get_azure_storage_service() -> AzureStorageService:
    """Get the Azure Storage service singleton."""
    global _azure_service
    if _azure_service is None:
        _azure_service = AzureStorageService()
    return _azure_service
