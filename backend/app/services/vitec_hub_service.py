"""
Vitec Hub Service

Handles authenticated requests to the Vitec Megler Hub API.
Rate-limited to stay well below Vitec's ~600 req/sec limit.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

# Shared rate limiter: min delay between requests (sec)
_vitec_rate_lock: asyncio.Lock | None = None
_vitec_last_request_at: float = 0.0


def _get_vitec_rate_lock() -> asyncio.Lock:
    global _vitec_rate_lock
    if _vitec_rate_lock is None:
        _vitec_rate_lock = asyncio.Lock()
    return _vitec_rate_lock


class VitecHubService:
    """Client for Vitec Hub API using Product Login."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        product_login: str | None = None,
        access_key: str | None = None,
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

    async def _request(self, method: str, path: str, *, accept: str = "application/json") -> Any:
        if not self.is_configured:
            raise HTTPException(
                status_code=500,
                detail="Vitec Hub credentials are not configured.",
            )

        # Rate limit: stay well below Vitec's ~600 req/sec
        global _vitec_last_request_at
        rps = max(1, min(settings.VITEC_RATE_LIMIT_REQUESTS_PER_SECOND, 200))
        min_interval = 1.0 / rps
        lock = _get_vitec_rate_lock()
        async with lock:
            now = time.monotonic()
            elapsed = now - _vitec_last_request_at
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            _vitec_last_request_at = time.monotonic()

        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(
                auth=self._get_auth(),
                timeout=30.0,
                headers={"Accept": accept},
            ) as client:
                response = await client.request(method, url)
        except httpx.HTTPError as exc:
            logger.error("Vitec Hub request failed: %s", exc)
            raise HTTPException(status_code=502, detail="Vitec Hub request failed.") from exc

        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Vitec Hub unauthorized.")
        if response.status_code == 403:
            raise HTTPException(status_code=403, detail="Vitec Hub forbidden.")
        if response.status_code == 404:
            return None  # Picture not found
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

        # Return raw bytes for image requests
        if accept.startswith("image/"):
            return response.content

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

    async def get_employee_picture(
        self,
        installation_id: str,
        employee_id: str | int,
    ) -> bytes | None:
        """
        Fetch employee profile picture.

        Args:
            installation_id: Vitec installation ID
            employee_id: Employee ID (vitec_employee_id)

        Returns:
            Image bytes or None if not found
        """
        return await self._request(
            "GET",
            f"{installation_id}/Employees/{employee_id}/Picture",
            accept="image/*",
        )

    async def get_department_picture(
        self,
        installation_id: str,
        department_id: str | int,
    ) -> bytes | None:
        """
        Fetch department banner/logo picture.

        Args:
            installation_id: Vitec installation ID
            department_id: Department ID (vitec_department_id)

        Returns:
            Image bytes or None if not found
        """
        return await self._request(
            "GET",
            f"{installation_id}/Departments/{department_id}/Picture",
            accept="image/*",
        )

    async def get_accounting_estates(
        self,
        installation_id: str,
        *,
        department_id: int | None = None,
        changed_after: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch estates relevant for accounting (oppdrag with sold/settlement status).

        Args:
            installation_id: Vitec installation ID
            department_id: Filter by department (e.g. 1120)
            changed_after: ISO datetime - only estates changed after this time

        Returns:
            List of AccountingEstateObject with brokersIdWithRoles, sold date, etc.
        """
        params: list[str] = []
        if department_id is not None:
            params.append(f"departmentId={department_id}")
        if changed_after:
            params.append(f"changedAfter={changed_after}")
        query = "&".join(params)
        path = f"{installation_id}/Accounting/Estates"
        if query:
            path = f"{path}?{query}"
        data = await self._request("GET", path)
        return list(data) if isinstance(data, list) else []

    async def get_accounting_transactions(
        self,
        installation_id: str,
        from_date: str,
        to_date: str,
        *,
        department_id: int | None = None,
        account_number: str | None = None,
        assignment_number: str | None = None,
        ledger_type: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Fetch booked accounting transactions (bokførte transaksjoner).

        Args:
            installation_id: Vitec installation ID
            from_date: Start date (ISO format)
            to_date: End date (ISO format)
            department_id: Filter by department (e.g. 1120)
            account_number: Filter by 4-digit hovedbokskonti
            assignment_number: Filter by oppdragsnummer
            ledger_type: 1=General (Hovedbok), 2=Customer, 3=Supplier

        Returns:
            List of AccountingTransaction with account, amount, estateId, userId
        """
        params = [f"fromDate={from_date}", f"toDate={to_date}", f"ledgerType={ledger_type}"]
        if department_id is not None:
            params.append(f"departmentId={department_id}")
        if account_number:
            params.append(f"accountNumber={account_number}")
        if assignment_number:
            params.append(f"assignmentNumber={assignment_number}")
        path = f"{installation_id}/Accounting/Transactions?{'&'.join(params)}"
        data = await self._request("GET", path)
        if isinstance(data, dict) and "transactions" in data:
            return list(data.get("transactions") or [])
        return []
