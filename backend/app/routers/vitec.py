"""
Vitec API Status and Connection Endpoints

Provides endpoints for checking Vitec Hub API configuration and connection status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.config import settings
from app.services.vitec_hub_service import VitecHubService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vitec", tags=["Vitec"])


class VitecStatusResponse(BaseModel):
    """Response model for Vitec API status check."""
    configured: bool
    connected: bool
    installation_id: Optional[str] = None
    error: Optional[str] = None
    available_methods: Optional[list[str]] = None


@router.get("/status", response_model=VitecStatusResponse)
async def get_vitec_status():
    """
    Check Vitec Hub API configuration and connection status.
    
    Returns:
        - configured: Whether credentials are present
        - connected: Whether a test API call succeeded
        - installation_id: The configured installation ID (masked)
        - error: Error message if connection failed
        - available_methods: Methods returned by Account/Methods if connected
    """
    hub = VitecHubService()
    
    # Check configuration
    if not hub.is_configured:
        return VitecStatusResponse(
            configured=False,
            connected=False,
            error="Vitec Hub credentials are not configured. Set VITEC_HUB_PRODUCT_LOGIN, VITEC_HUB_ACCESS_KEY, and VITEC_HUB_BASE_URL environment variables.",
        )
    
    # Get installation ID (masked for security)
    installation_id = settings.VITEC_INSTALLATION_ID
    masked_id = None
    if installation_id:
        # Show first 4 and last 4 characters
        if len(installation_id) > 8:
            masked_id = f"{installation_id[:4]}...{installation_id[-4:]}"
        else:
            masked_id = installation_id
    
    # Test connection by calling Account/Methods
    try:
        methods_data = await hub.get_methods()
        method_names = [m.get("name", str(m)) for m in methods_data] if methods_data else []
        
        return VitecStatusResponse(
            configured=True,
            connected=True,
            installation_id=masked_id,
            available_methods=method_names,
        )
    except HTTPException as e:
        logger.warning(f"Vitec Hub connection test failed: {e.detail}")
        return VitecStatusResponse(
            configured=True,
            connected=False,
            installation_id=masked_id,
            error=e.detail,
        )
    except Exception as e:
        logger.error(f"Unexpected error testing Vitec Hub connection: {e}")
        return VitecStatusResponse(
            configured=True,
            connected=False,
            installation_id=masked_id,
            error=f"Connection test failed: {str(e)}",
        )
