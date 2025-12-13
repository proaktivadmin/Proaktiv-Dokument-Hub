"""
Analytics API Routes

Dashboard statistics and metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.template import Template
from app.models.category import Category
from app.models.audit_log import AuditLog

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics from the database."""
    
    # Count templates by status
    total_query = select(func.count(Template.id))
    total = await db.scalar(total_query) or 0
    
    published_query = select(func.count(Template.id)).where(Template.status == "published")
    published = await db.scalar(published_query) or 0
    
    draft_query = select(func.count(Template.id)).where(Template.status == "draft")
    draft = await db.scalar(draft_query) or 0
    
    archived_query = select(func.count(Template.id)).where(Template.status == "archived")
    archived = await db.scalar(archived_query) or 0
    
    # Count downloads in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    downloads_query = (
        select(func.count(AuditLog.id))
        .where(AuditLog.action == "downloaded")
        .where(AuditLog.timestamp >= thirty_days_ago)
    )
    downloads = await db.scalar(downloads_query) or 0
    
    # Get recent uploads
    recent_query = (
        select(Template)
        .where(Template.status != "archived")
        .order_by(Template.created_at.desc())
        .limit(5)
    )
    recent_result = await db.execute(recent_query)
    recent_templates = recent_result.scalars().all()
    
    # Get categories with template counts
    categories = await db.execute(select(Category).order_by(Category.sort_order))
    categories_list = categories.scalars().all()
    
    # Build categories breakdown (simplified - would need join for accurate counts)
    categories_breakdown = {cat.name: 0 for cat in categories_list}
    
    return {
        "total_templates": total,
        "published_templates": published,
        "draft_templates": draft,
        "archived_templates": archived,
        "total_downloads_30d": downloads,
        "most_downloaded": [],  # Would require aggregating audit logs
        "recent_uploads": [
            {
                "template_id": str(t.id),
                "title": t.title,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in recent_templates
        ],
        "categories_breakdown": categories_breakdown
    }

