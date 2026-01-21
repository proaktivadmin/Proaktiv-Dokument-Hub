"""
Tag API Routes

Handles tag CRUD operations with database integration.
"""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.tag_service import TagService

router = APIRouter()


@router.get("")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """List all tags."""
    tags = await TagService.get_all(db)
    return {
        "tags": [
            {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat() if tag.created_at else None,
            }
            for tag in tags
        ]
    }


@router.post("", status_code=201)
async def create_tag(
    db: AsyncSession = Depends(get_db), name: str = Body(..., embed=True), color: str = Body("#3B82F6", embed=True)
):
    """Create a new tag."""
    try:
        tag = await TagService.create(db, name=name, color=color)
        return {
            "id": str(tag.id),
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tag_id}")
async def update_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
    name: str | None = Body(None, embed=True),
    color: str | None = Body(None, embed=True),
):
    """Update a tag."""
    tag = await TagService.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    updates = {}
    if name is not None:
        updates["name"] = name
    if color is not None:
        updates["color"] = color

    try:
        tag = await TagService.update(db, tag, **updates)
        return {"id": str(tag.id), "name": tag.name, "color": tag.color}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a tag."""
    tag = await TagService.get_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    await TagService.delete(db, tag)
    return None
