"""
Vitec Hub Service

Handles authenticated requests to the Vitec Megler Hub API.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class VitecHubService:
    """Client for Vitec Hub API using Product Login."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        product_login: Optional[str] = None,
        access_key: Optional[str] = None,
    ) -> None:
        self._base_url = (base_url or settings.VITEC_HUB_BASE_URL or self._derive_base_url()).rstrip("/")
        self._product_login = product_login or settings.VITEC_HUB_PRODUCT_LOGIN
        self._access_key = access_key or settings.VITEC_HUB_ACCESS_KEY or settings.VITEC_ACCESS_KEY

    @property
    def is_configured(self) -> bool:
        """Return True when base URL and credentials are present."""
        return bool(self._base_url and self._product_login and self._access_key)

    def _derive_base_url(self) -> str:
        env = (settings.VITEC_ENVIRONMENT or "").lower()
        if env in ("prod", "production"):
            return "https://hub.megler.vitec.net"
        if env in ("qa", "test", "testing"):
            return "https://hub.qa.vitecnext.no"
        return ""

    def _get_auth(self) -> httpx.BasicAuth:
        return httpx.BasicAuth(self._product_login, self._access_key)

    async def _request(self, method: str, path: str) -> Any:
        if not self.is_configured:
            raise HTTPException(
                status_code=500,
                detail="Vitec Hub credentials are not configured.",
            )

        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(
                auth=self._get_auth(),
                timeout=30.0,
                headers={"Accept": "application/json"},
            ) as client:
                response = await client.request(method, url)
        except httpx.HTTPError as exc:
            logger.error("Vitec Hub request failed: %s", exc)
            raise HTTPException(status_code=502, detail="Vitec Hub request failed.") from exc

        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Vitec Hub unauthorized.")
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="Vitec Hub forbidden.")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            detail = "Vitec Hub rate limit reached."
            if retry_after:
                detail = f"{detail} Retry after {retry_after} seconds."
            raise HTTPException(status_code=429, detail=detail)
        if response.is_error:
            message = response.text.strip()[:500]
            raise HTTPException(
                status_code=502,
                detail=f"Vitec Hub error {response.status_code}: {message}",
            )

        try:
            return response.json()
        except ValueError as exc:
            logger.error("Failed to parse Vitec Hub response JSON: %s", exc)
            raise HTTPException(status_code=502, detail="Invalid Vitec Hub response.") from exc

    async def get_methods(self) -> list[dict[str, Any]]:
        """List available functions for the product login."""
        data = await self._request("GET", "Account/Methods")
        return list(data or [])

    async def get_departments(self, installation_id: str) -> list[dict[str, Any]]:
        """Fetch offices (departments) for a specific installation."""
        data = await self._request("GET", f"{installation_id}/Departments")
        return list(data or [])

    async def get_employees(self, installation_id: str) -> list[dict[str, Any]]:
        """Fetch employees for a specific installation."""
        data = await self._request("GET", f"{installation_id}/Employees")
        return list(data or [])
