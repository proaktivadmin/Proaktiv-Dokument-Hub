"""
Microsoft Graph API Client

Integration with Microsoft 365 for Teams and SharePoint operations.
"""

import logging
from typing import Any

import httpx
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Response Models
# =============================================================================


class TeamsGroup(BaseModel):
    """Teams group/team representation."""

    id: str
    display_name: str
    description: str | None = None
    mail: str | None = None


class TeamMember(BaseModel):
    """Team member representation."""

    id: str
    display_name: str
    email: str | None = None


# =============================================================================
# Microsoft Graph Client
# =============================================================================


class MicrosoftGraphClient:
    """
    Client for Microsoft Graph API operations.

    Supports:
    - Teams groups listing
    - Team membership queries
    - Email sending via Exchange

    Uses client credentials flow (service account).
    """

    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        self._access_token: str | None = None

    @property
    def is_configured(self) -> bool:
        """Check if Microsoft Graph credentials are configured."""
        return bool(self.tenant_id and self.client_id and self.client_secret and self.tenant_id != "placeholder")

    async def _get_access_token(self) -> str:
        """Get access token using client credentials flow."""
        if not self.is_configured:
            raise ValueError("Microsoft Graph credentials not configured")

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "https://graph.microsoft.com/.default",
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make authenticated request to Graph API."""
        if not self._access_token:
            self._access_token = await self._get_access_token()

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                **kwargs,
            )
            response.raise_for_status()
            return response.json() if response.content else {}

    # =========================================================================
    # Teams Operations
    # =========================================================================

    async def list_teams(self) -> list[TeamsGroup]:
        """
        List all Teams groups the service account has access to.

        Returns:
            List of TeamsGroup objects
        """
        if not self.is_configured:
            logger.warning("Microsoft Graph not configured, returning empty list")
            return []

        try:
            data = await self._request("GET", "/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')")
            return [
                TeamsGroup(
                    id=g["id"],
                    display_name=g["displayName"],
                    description=g.get("description"),
                    mail=g.get("mail"),
                )
                for g in data.get("value", [])
            ]
        except Exception as e:
            logger.error(f"Failed to list Teams: {e}")
            return []

    async def get_team_members(self, team_id: str) -> list[TeamMember]:
        """
        Get members of a specific team.

        Args:
            team_id: The Teams group ID

        Returns:
            List of TeamMember objects
        """
        if not self.is_configured:
            return []

        try:
            data = await self._request("GET", f"/groups/{team_id}/members")
            return [
                TeamMember(
                    id=m["id"],
                    display_name=m.get("displayName", ""),
                    email=m.get("mail"),
                )
                for m in data.get("value", [])
            ]
        except Exception as e:
            logger.error(f"Failed to get team members: {e}")
            return []

    # =========================================================================
    # Email Operations
    # =========================================================================

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        *,
        from_address: str | None = None,
        is_html: bool = False,
    ) -> bool:
        """
        Send email via Microsoft Graph.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            from_address: Sender address (must be authorized)
            is_html: Whether body is HTML

        Returns:
            True if sent successfully
        """
        if not self.is_configured:
            logger.warning("Microsoft Graph not configured, email not sent")
            return False

        sender = from_address or settings.MICROSOFT_SENDER_EMAIL
        if not sender:
            logger.error("No sender email configured")
            return False

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body,
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to],
            },
            "saveToSentItems": "true",
        }

        try:
            await self._request(
                "POST",
                f"/users/{sender}/sendMail",
                json=message,
            )
            logger.info(f"Email sent to {len(to)} recipients")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Singleton instance
graph_client = MicrosoftGraphClient()
