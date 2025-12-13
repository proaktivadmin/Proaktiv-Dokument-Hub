"""
Audit Service - Logging user actions for compliance.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
import logging

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service class for audit log operations.
    """
    
    @staticmethod
    async def log(
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: UUID,
        action: str,
        user_email: str,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            entity_type: Type of entity (template, tag, category)
            entity_id: Entity UUID
            action: Action performed (created, updated, deleted, published, downloaded)
            user_email: User who performed the action
            details: Additional context
            
        Returns:
            Created audit log entry
        """
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_email=user_email,
            details=details or {}
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        
        logger.debug(f"Audit: {action} {entity_type}:{entity_id} by {user_email}")
        return audit_log
    
    @staticmethod
    async def get_for_entity(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity
            entity_id: Entity UUID
            limit: Max number of entries to return
            
        Returns:
            List of audit log entries
        """
        query = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_recent(
        db: AsyncSession,
        *,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        user_email: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get recent audit logs with optional filters.
        
        Args:
            db: Database session
            entity_type: Filter by entity type
            action: Filter by action
            user_email: Filter by user
            since: Filter by timestamp
            limit: Max number of entries
            
        Returns:
            List of audit log entries
        """
        query = select(AuditLog).order_by(AuditLog.timestamp.desc())
        
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
        if action:
            query = query.where(AuditLog.action == action)
        if user_email:
            query = query.where(AuditLog.user_email == user_email)
        if since:
            query = query.where(AuditLog.timestamp >= since)
        
        query = query.limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

