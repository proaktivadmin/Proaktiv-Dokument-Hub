"""
Dashboard Service - Statistics and analytics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging

from app.models.template import Template
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service for dashboard statistics and analytics.
    """
    
    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """
        Get dashboard statistics.
        
        Returns:
            Dict containing:
            - total: Total template count
            - published: Published template count
            - draft: Draft template count
            - archived: Archived template count
            - downloads: Total download count from audit log
            - recent_uploads: List of 5 most recent templates
        """
        # Get template counts by status
        total_result = await db.execute(
            select(func.count(Template.id))
        )
        total = total_result.scalar() or 0
        
        published_result = await db.execute(
            select(func.count(Template.id)).where(Template.status == 'published')
        )
        published = published_result.scalar() or 0
        
        draft_result = await db.execute(
            select(func.count(Template.id)).where(Template.status == 'draft')
        )
        draft = draft_result.scalar() or 0
        
        archived_result = await db.execute(
            select(func.count(Template.id)).where(Template.status == 'archived')
        )
        archived = archived_result.scalar() or 0
        
        # Get download count from audit log
        downloads = await DashboardService.get_download_count(db)
        
        # Get recent uploads
        recent_uploads = await DashboardService.get_recent_uploads(db, limit=5)
        
        return {
            'total': total,
            'published': published,
            'draft': draft,
            'archived': archived,
            'downloads': downloads,
            'recent_uploads': recent_uploads
        }
    
    @staticmethod
    async def get_recent_uploads(
        db: AsyncSession,
        limit: int = 5
    ) -> List[dict]:
        """
        Get most recently uploaded templates.
        
        Args:
            db: Database session
            limit: Maximum number of results
            
        Returns:
            List of template summary dicts
        """
        result = await db.execute(
            select(Template.id, Template.title, Template.created_at)
            .order_by(Template.created_at.desc())
            .limit(limit)
        )
        
        templates = result.all()
        
        return [
            {
                'id': str(template.id),
                'title': template.title,
                'created_at': template.created_at.isoformat()
            }
            for template in templates
        ]
    
    @staticmethod
    async def get_download_count(db: AsyncSession) -> int:
        """
        Get total download count from audit log.
        
        Args:
            db: Database session
            
        Returns:
            Total download count
        """
        result = await db.execute(
            select(func.count(AuditLog.id))
            .where(AuditLog.action == 'download')
        )
        
        count = result.scalar() or 0
        return count
