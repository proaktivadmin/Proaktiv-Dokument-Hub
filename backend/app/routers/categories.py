"""
Category API Routes

Handles category CRUD operations with database integration.
"""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all categories sorted by sort_order."""
    categories = await CategoryService.get_all(db)
    return {
        "categories": [
            {
                "id": str(cat.id),
                "name": cat.name,
                "icon": cat.icon,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
            }
            for cat in categories
        ]
    }


@router.post("", status_code=201)
async def create_category(
    db: AsyncSession = Depends(get_db),
    name: str = Body(..., embed=True),
    icon: str | None = Body(None, embed=True),
    description: str | None = Body(None, embed=True),
    sort_order: int | None = Body(None, embed=True),
):
    """Create a new category."""
    try:
        category = await CategoryService.create(
            db, name=name, icon=icon, description=description, sort_order=sort_order
        )
        return {
            "id": str(category.id),
            "name": category.name,
            "icon": category.icon,
            "description": category.description,
            "sort_order": category.sort_order,
            "created_at": category.created_at.isoformat() if category.created_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}")
async def update_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    name: str | None = Body(None, embed=True),
    icon: str | None = Body(None, embed=True),
    description: str | None = Body(None, embed=True),
    sort_order: int | None = Body(None, embed=True),
):
    """Update a category."""
    category = await CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    updates = {}
    if name is not None:
        updates["name"] = name
    if icon is not None:
        updates["icon"] = icon
    if description is not None:
        updates["description"] = description
    if sort_order is not None:
        updates["sort_order"] = sort_order

    try:
        category = await CategoryService.update(db, category, **updates)
        return {
            "id": str(category.id),
            "name": category.name,
            "icon": category.icon,
            "description": category.description,
            "sort_order": category.sort_order,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a category."""
    category = await CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await CategoryService.delete(db, category)
    return None


@router.post("/reorder")
async def reorder_categories(db: AsyncSession = Depends(get_db), category_ids: list[UUID] = Body(..., embed=True)):
    """Reorder categories by providing ordered list of IDs."""
    categories = await CategoryService.reorder(db, category_ids)
    return {"categories": [{"id": str(cat.id), "name": cat.name, "sort_order": cat.sort_order} for cat in categories]}
