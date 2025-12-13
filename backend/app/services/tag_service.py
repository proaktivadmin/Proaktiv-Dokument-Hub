"""
Tag Service - Business logic for tag operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
import logging

from app.models.tag import Tag

logger = logging.getLogger(__name__)


class TagService:
    """
    Service class for tag CRUD operations.
    """
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Tag]:
        """
        Get all tags.
        
        Args:
            db: Database session
            
        Returns:
            List of all tags
        """
        query = select(Tag).order_by(Tag.name)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(db: AsyncSession, tag_id: UUID) -> Optional[Tag]:
        """
        Get a tag by ID.
        
        Args:
            db: Database session
            tag_id: Tag UUID
            
        Returns:
            Tag or None if not found
        """
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Tag]:
        """
        Get a tag by name.
        
        Args:
            db: Database session
            name: Tag name
            
        Returns:
            Tag or None if not found
        """
        query = select(Tag).where(Tag.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        color: str = "#3B82F6"
    ) -> Tag:
        """
        Create a new tag.
        
        Args:
            db: Database session
            name: Tag name (must be unique)
            color: Hex color code
            
        Returns:
            Created tag
            
        Raises:
            ValueError: If tag name already exists
        """
        # Check for existing tag
        existing = await TagService.get_by_name(db, name)
        if existing:
            raise ValueError(f"Tag '{name}' already exists")
        
        tag = Tag(name=name, color=color)
        db.add(tag)
        
        try:
            await db.commit()
            await db.refresh(tag)
            logger.info(f"Created tag: {tag.id} - {tag.name}")
            return tag
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Tag '{name}' already exists")
    
    @staticmethod
    async def update(
        db: AsyncSession,
        tag: Tag,
        **updates
    ) -> Tag:
        """
        Update a tag.
        
        Args:
            db: Database session
            tag: Tag to update
            **updates: Fields to update
            
        Returns:
            Updated tag
        """
        for key, value in updates.items():
            if hasattr(tag, key) and value is not None:
                setattr(tag, key, value)
        
        try:
            await db.commit()
            await db.refresh(tag)
            logger.info(f"Updated tag: {tag.id}")
            return tag
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Tag name already exists")
    
    @staticmethod
    async def delete(db: AsyncSession, tag: Tag) -> None:
        """
        Delete a tag.
        
        Args:
            db: Database session
            tag: Tag to delete
        """
        await db.delete(tag)
        await db.commit()
        logger.info(f"Deleted tag: {tag.id}")

