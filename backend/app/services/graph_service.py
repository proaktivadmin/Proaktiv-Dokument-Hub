"""
Graph Service - Microsoft Graph email sender for signature notifications.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)


class GraphService:
    """Service for Microsoft Graph mail operations."""

    TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    SEND_MAIL_URL = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"

    @staticmethod
    def _get_credentials() -> tuple[str, str, str]:
        tenant_id = os.environ.get("ENTRA_TENANT_ID", "").strip()
        client_id = os.environ.get("ENTRA_CLIENT_ID", "").strip()
        client_secret = os.environ.get("ENTRA_CLIENT_SECRET", "").strip()
        return tenant_id, client_id, client_secret

    @staticmethod
    async def get_access_token() -> str:
        """Get Graph access token using client credentials flow."""
        tenant_id, client_id, client_secret = GraphService._get_credentials()
        if not tenant_id or not client_id or not client_secret:
            logger.error("Missing ENTRA Graph credentials; cannot request access token.")
            return ""

        token_url = GraphService.TOKEN_URL.format(tenant_id=tenant_id)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    token_url,
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "scope": "https://graph.microsoft.com/.default",
                        "grant_type": "client_credentials",
                    },
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Graph token request failed (status %s): %s",
                exc.response.status_code,
                exc.response.text,
            )
            return ""
        except httpx.HTTPError as exc:
            logger.error("Graph token request failed: %s", exc)
            return ""

        token = data.get("access_token")
        if not token:
            logger.error("Graph token response missing access_token.")
            return ""

        return token

    @staticmethod
    async def send_mail(
        sender_email: str,
        recipient_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """Send an email using Microsoft Graph."""
        token = await GraphService.get_access_token()
        if not token:
            return False

        if not sender_email or not recipient_email:
            logger.error("Sender or recipient email missing; cannot send mail.")
            return False

        sender_encoded = quote(sender_email)
        send_url = GraphService.SEND_MAIL_URL.format(sender=sender_encoded)

        payload = {
            "message": {
                "subject": subject,
                "body": {"contentType": "HTML", "content": html_body},
                "toRecipients": [{"emailAddress": {"address": recipient_email}}],
            },
            "saveToSentItems": True,
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(send_url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Graph sendMail failed (status %s): %s",
                exc.response.status_code,
                exc.response.text,
            )
            return False
        except httpx.HTTPError as exc:
            logger.error("Graph sendMail request failed: %s", exc)
            return False

        logger.info("Signature notification email sent to %s", recipient_email)
        return True
