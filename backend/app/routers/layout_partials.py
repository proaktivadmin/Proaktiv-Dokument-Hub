"""
Layout Partials API Routes
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
from uuid import UUID

from app.database import get_db
from app.services.layout_partial_service import LayoutPartialService
from app.schemas.layout_partial import (
    LayoutPartialCreate,
    LayoutPartialUpdate,
    LayoutPartialResponse,
    LayoutPartialListResponse,
    LayoutPartialSetDefaultResponse
)

router = APIRouter(prefix="/layout-partials", tags=["Layout Partials"])


def get_current_user_email(x_user_email: str = Header(default="system@proaktiv.no")) -> str:
    """Get current user email from header or default."""
    return x_user_email


@router.get("", response_model=LayoutPartialListResponse)
async def list_layout_partials(
    db: AsyncSession = Depends(get_db),
    type: Optional[Literal['header', 'footer']] = Query(None),
    context: Optional[Literal['pdf', 'email', 'all']] = Query(None)
):
    """List all layout partials with optional filters."""
    partials = await LayoutPartialService.get_list(
        db,
        type_filter=type,
        context_filter=context
    )
    
    return LayoutPartialListResponse(
        partials=[LayoutPartialResponse.model_validate(p) for p in partials],
        total=len(partials)
    )


@router.get("/default", response_model=LayoutPartialResponse)
async def get_default_partial(
    type: Literal['header', 'footer'] = Query(...),
    context: Literal['pdf', 'email', 'all'] = Query('all'),
    db: AsyncSession = Depends(get_db)
):
    """Get the default partial for a type/context combination."""
    partial = await LayoutPartialService.get_default(
        db,
        type_filter=type,
        context_filter=context
    )
    if not partial:
        raise HTTPException(status_code=404, detail="No default partial found")
    return LayoutPartialResponse.model_validate(partial)


@router.get("/{partial_id}", response_model=LayoutPartialResponse)
async def get_layout_partial(
    partial_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a layout partial by ID."""
    partial = await LayoutPartialService.get_by_id(db, partial_id)
    if not partial:
        raise HTTPException(status_code=404, detail="Layout partial not found")
    return LayoutPartialResponse.model_validate(partial)


@router.post("", response_model=LayoutPartialResponse, status_code=201)
async def create_layout_partial(
    body: LayoutPartialCreate,
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """Create a new layout partial."""
    partial = await LayoutPartialService.create(
        db,
        name=body.name,
        type=body.type,
        context=body.context,
        html_content=body.html_content,
        is_default=body.is_default,
        created_by=user_email
    )
    return LayoutPartialResponse.model_validate(partial)


@router.put("/{partial_id}", response_model=LayoutPartialResponse)
async def update_layout_partial(
    partial_id: UUID,
    body: LayoutPartialUpdate,
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user_email)
):
    """Update a layout partial."""
    partial = await LayoutPartialService.get_by_id(db, partial_id)
    if not partial:
        raise HTTPException(status_code=404, detail="Layout partial not found")
    
    partial = await LayoutPartialService.update(
        db,
        partial,
        updated_by=user_email,
        **body.model_dump(exclude_unset=True)
    )
    return LayoutPartialResponse.model_validate(partial)


@router.delete("/{partial_id}", status_code=204)
async def delete_layout_partial(
    partial_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a layout partial."""
    partial = await LayoutPartialService.get_by_id(db, partial_id)
    if not partial:
        raise HTTPException(status_code=404, detail="Layout partial not found")
    
    await LayoutPartialService.delete(db, partial)
    return None


@router.post("/{partial_id}/set-default", response_model=LayoutPartialSetDefaultResponse)
async def set_default_partial(
    partial_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Set a partial as the default for its type/context."""
    partial = await LayoutPartialService.get_by_id(db, partial_id)
    if not partial:
        raise HTTPException(status_code=404, detail="Layout partial not found")
    
    previous_default_id = await LayoutPartialService.set_default(db, partial)
    
    return LayoutPartialSetDefaultResponse(
        id=partial.id,
        is_default=True,
        previous_default_id=previous_default_id
    )
