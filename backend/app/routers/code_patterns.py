"""
Code Patterns API Routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.code_pattern import CodePatternCreate, CodePatternListResponse, CodePatternResponse, CodePatternUpdate
from app.services.code_pattern_service import CodePatternService

router = APIRouter(prefix="/code-patterns", tags=["Code Patterns"])


def get_current_user_email(x_user_email: str = Header(default="system@proaktiv.no")) -> str:
    """Get current user email from header or default."""
    return x_user_email


@router.get("", response_model=CodePatternListResponse)
async def list_code_patterns(
    db: AsyncSession = Depends(get_db),
    category: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List all code patterns with optional filters."""
    patterns, total = await CodePatternService.get_list(
        db, category=category, search=search, page=page, per_page=per_page
    )

    return CodePatternListResponse(
        patterns=[CodePatternResponse.model_validate(p) for p in patterns],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page if total > 0 else 0,
    )


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all unique categories."""
    categories = await CodePatternService.get_categories(db)
    return {"categories": categories}


@router.get("/{pattern_id}", response_model=CodePatternResponse)
async def get_code_pattern(pattern_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a code pattern by ID."""
    pattern = await CodePatternService.get_by_id(db, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Code pattern not found")
    return CodePatternResponse.model_validate(pattern)


@router.post("", response_model=CodePatternResponse, status_code=201)
async def create_code_pattern(
    body: CodePatternCreate, db: AsyncSession = Depends(get_db), user_email: str = Depends(get_current_user_email)
):
    """Create a new code pattern."""
    pattern = await CodePatternService.create(
        db,
        name=body.name,
        category=body.category,
        html_code=body.html_code,
        description=body.description,
        variables_used=body.variables_used,
        created_by=user_email,
    )
    return CodePatternResponse.model_validate(pattern)


@router.put("/{pattern_id}", response_model=CodePatternResponse)
async def update_code_pattern(
    pattern_id: UUID,
    body: CodePatternUpdate,
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user_email),
):
    """Update a code pattern."""
    pattern = await CodePatternService.get_by_id(db, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Code pattern not found")

    pattern = await CodePatternService.update(db, pattern, updated_by=user_email, **body.model_dump(exclude_unset=True))
    return CodePatternResponse.model_validate(pattern)


@router.delete("/{pattern_id}", status_code=204)
async def delete_code_pattern(pattern_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a code pattern."""
    pattern = await CodePatternService.get_by_id(db, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Code pattern not found")

    await CodePatternService.delete(db, pattern)
    return None


@router.post("/{pattern_id}/increment-usage", status_code=204)
async def increment_usage(pattern_id: UUID, db: AsyncSession = Depends(get_db)):
    """Increment usage count for a code pattern."""
    pattern = await CodePatternService.get_by_id(db, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Code pattern not found")

    await CodePatternService.increment_usage(db, pattern_id)
    return None
