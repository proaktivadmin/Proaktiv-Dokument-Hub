"""
Category Service - Business logic for category operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from uuid import UUID
import logging

from app.models.category import Category

logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service class for category CRUD operations.
    """
    
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Category]:
        """
        Get all categories sorted by sort_order.
        
        Args:
            db: Database session
            
        Returns:
            List of all categories
        """
        query = select(Category).order_by(Category.sort_order, Category.name)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: UUID) -> Optional[Category]:
        """
        Get a category by ID.
        
        Args:
            db: Database session
            category_id: Category UUID
            
        Returns:
            Category or None if not found
        """
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Category]:
        """
        Get a category by name.
        
        Args:
            db: Database session
            name: Category name
            
        Returns:
            Category or None if not found
        """
        query = select(Category).where(Category.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        name: str,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: Optional[int] = None
    ) -> Category:
        """
        Create a new category.
        
        Args:
            db: Database session
            name: Category name (must be unique)
            icon: Lucide icon name
            description: Category description
            sort_order: Display order (auto-assigned if not provided)
            
        Returns:
            Created category
            
        Raises:
            ValueError: If category name already exists
        """
        # Check for existing category
        existing = await CategoryService.get_by_name(db, name)
        if existing:
            raise ValueError(f"Category '{name}' already exists")
        
        # Auto-assign sort_order if not provided
        if sort_order is None:
            max_order_query = select(func.max(Category.sort_order))
            result = await db.execute(max_order_query)
            max_order = result.scalar() or 0
            sort_order = max_order + 1
        
        category = Category(
            name=name,
            icon=icon,
            description=description,
            sort_order=sort_order
        )
        db.add(category)
        
        try:
            await db.commit()
            await db.refresh(category)
            logger.info(f"Created category: {category.id} - {category.name}")
            return category
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Category '{name}' already exists")
    
    @staticmethod
    async def update(
        db: AsyncSession,
        category: Category,
        **updates
    ) -> Category:
        """
        Update a category.
        
        Args:
            db: Database session
            category: Category to update
            **updates: Fields to update
            
        Returns:
            Updated category
        """
        for key, value in updates.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)
        
        try:
            await db.commit()
            await db.refresh(category)
            logger.info(f"Updated category: {category.id}")
            return category
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Category name already exists")
    
    @staticmethod
    async def delete(db: AsyncSession, category: Category) -> None:
        """
        Delete a category.
        
        Args:
            db: Database session
            category: Category to delete
        """
        await db.delete(category)
        await db.commit()
        logger.info(f"Deleted category: {category.id}")
    
    @staticmethod
    async def reorder(
        db: AsyncSession,
        category_ids: List[UUID]
    ) -> List[Category]:
        """
        Reorder categories based on the provided ID order.
        
        Args:
            db: Database session
            category_ids: List of category IDs in desired order
            
        Returns:
            Updated categories
        """
        categories = []
        for index, cat_id in enumerate(category_ids):
            category = await CategoryService.get_by_id(db, cat_id)
            if category:
                category.sort_order = index
                categories.append(category)
        
        await db.commit()
        logger.info(f"Reordered {len(categories)} categories")
        return categories

