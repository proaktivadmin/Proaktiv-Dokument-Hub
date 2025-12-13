"""
Sanitizer Router - API endpoints for HTML sanitization.

Provides endpoints for cleaning and validating HTML templates
for Vitec Next compatibility.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.sanitizer_service import SanitizerService, get_sanitizer_service


router = APIRouter(prefix="/api/sanitize", tags=["sanitizer"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SanitizeRequest(BaseModel):
    """Request model for sanitization endpoints."""
    
    html: str = Field(
        ...,
        description="The raw HTML content to sanitize",
        min_length=1
    )
    update_resource: bool = Field(
        default=True,
        description="Whether to update Vitec resource pointers to the new stylesheet"
    )
    theme_class: str = Field(
        default="proaktiv-theme",
        description="The CSS class to apply to the wrapper div"
    )


class SanitizeResponse(BaseModel):
    """Response model for sanitization endpoints."""
    
    html: str = Field(..., description="The sanitized HTML content")
    original_length: int = Field(..., description="Length of the original HTML")
    sanitized_length: int = Field(..., description="Length of the sanitized HTML")


class ValidateRequest(BaseModel):
    """Request model for validation endpoint."""
    
    html: str = Field(
        ...,
        description="The HTML content to validate",
        min_length=1
    )


class ValidateResponse(BaseModel):
    """Response model for validation endpoint."""
    
    has_vitec_wrapper: bool = Field(
        ...,
        description="Whether the HTML has a #vitecTemplate wrapper"
    )
    has_resource_reference: bool = Field(
        ...,
        description="Whether the HTML has a Vitec resource reference"
    )
    has_legacy_font_tags: bool = Field(
        ...,
        description="Whether the HTML contains deprecated <font> tags"
    )
    legacy_style_count: int = Field(
        ...,
        description="Number of elements with legacy inline styles"
    )
    is_valid: bool = Field(
        ...,
        description="Whether the template is fully valid for Vitec"
    )


class StripStylesRequest(BaseModel):
    """Request model for style stripping endpoint."""
    
    html: str = Field(
        ...,
        description="The HTML content to strip styles from",
        min_length=1
    )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/preview", response_model=SanitizeResponse)
async def sanitize_preview(
    request: SanitizeRequest,
    service: SanitizerService = Depends(get_sanitizer_service)
) -> SanitizeResponse:
    """
    Sanitize HTML for preview purposes.
    
    This endpoint:
    - Strips legacy inline styles (font-family, font-size, color, background-color)
    - Removes deprecated <font> tags while preserving content
    - Updates Vitec resource pointers to the new stylesheet
    - Ensures content is wrapped in a standard #vitecTemplate wrapper
    
    Args:
        request: The sanitization request containing raw HTML.
        service: The injected SanitizerService instance.
        
    Returns:
        The sanitized HTML with metadata.
        
    Raises:
        HTTPException: If sanitization fails.
    """
    try:
        # Create a service with custom theme class if provided
        if request.theme_class != "proaktiv-theme":
            custom_service = SanitizerService(theme_class=request.theme_class)
            sanitized = custom_service.sanitize(
                request.html,
                update_resource=request.update_resource
            )
        else:
            sanitized = service.sanitize(
                request.html,
                update_resource=request.update_resource
            )
        
        return SanitizeResponse(
            html=sanitized,
            original_length=len(request.html),
            sanitized_length=len(sanitized)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sanitize HTML: {str(e)}"
        )


@router.post("/validate", response_model=ValidateResponse)
async def validate_template(
    request: ValidateRequest,
    service: SanitizerService = Depends(get_sanitizer_service)
) -> ValidateResponse:
    """
    Validate an HTML template for Vitec compatibility.
    
    Checks for:
    - Presence of #vitecTemplate wrapper
    - Vitec resource references
    - Legacy <font> tags
    - Legacy inline styles
    
    Args:
        request: The validation request containing HTML to validate.
        service: The injected SanitizerService instance.
        
    Returns:
        Validation results with detailed checks.
        
    Raises:
        HTTPException: If validation fails.
    """
    try:
        result = service.validate_structure(request.html)
        return ValidateResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate HTML: {str(e)}"
        )


@router.post("/strip-styles", response_model=SanitizeResponse)
async def strip_styles(
    request: StripStylesRequest,
    service: SanitizerService = Depends(get_sanitizer_service)
) -> SanitizeResponse:
    """
    Strip only inline styles without other processing.
    
    Useful for partial cleanup operations where you want to remove
    legacy styles but preserve the document structure.
    
    Args:
        request: The request containing HTML to process.
        service: The injected SanitizerService instance.
        
    Returns:
        The HTML with inline styles removed.
        
    Raises:
        HTTPException: If style stripping fails.
    """
    try:
        result = service.strip_styles_only(request.html)
        return SanitizeResponse(
            html=result,
            original_length=len(request.html),
            sanitized_length=len(result)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to strip styles: {str(e)}"
        )
