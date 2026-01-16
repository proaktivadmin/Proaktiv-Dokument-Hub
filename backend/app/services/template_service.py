"""
Template Service - Business logic for template operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from uuid import UUID
import logging

from app.models.template import Template, TemplateVersion
from app.models.tag import Tag
from app.models.category import Category

logger = logging.getLogger(__name__)


class TemplateService:
    """
    Service class for template CRUD operations.
    
    All database operations are performed through this service.
    """
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        *,
        status: Optional[str] = None,
        search: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        category_id: Optional[UUID] = None,
        category_ids: Optional[List[UUID]] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "updated_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Template], int]:
        """
        Get paginated list of templates with filters.
        
        Args:
            db: Database session
            status: Filter by status (draft, published, archived)
            search: Search in title/description
            tag_ids: Filter by tag IDs
            category_id: Filter by a single category ID
            category_ids: Filter by multiple category IDs
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: asc or desc
            
        Returns:
            Tuple of (templates list, total count)
        """
        # Base query with relationships
        query = select(Template).options(
            selectinload(Template.tags),
            selectinload(Template.categories)
        )
        
        # Apply filters
        if status:
            query = query.where(Template.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Template.title.ilike(search_pattern),
                    Template.description.ilike(search_pattern)
                )
            )
        
        if tag_ids:
            query = query.join(Template.tags).where(Tag.id.in_(tag_ids))
        
        # Handle single category_id or multiple category_ids
        if category_id:
            query = query.join(Template.categories).where(Category.id == category_id)
        elif category_ids:
            query = query.join(Template.categories).where(Category.id.in_(category_ids))
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        
        # Apply sorting
        sort_column = getattr(Template, sort_by, Template.updated_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Execute
        result = await db.execute(query)
        templates = result.scalars().unique().all()
        
        return list(templates), total
    
    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: UUID) -> Optional[Template]:
        """
        Get a template by ID with all relationships.
        
        Args:
            db: Database session
            template_id: Template UUID
            
        Returns:
            Template or None if not found
        """
        # Convert UUID to string for SQLite compatibility
        template_id_str = str(template_id)
        
        query = select(Template).options(
            selectinload(Template.tags),
            selectinload(Template.categories),
            selectinload(Template.versions)
        ).where(Template.id == template_id_str)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        title: str,
        file_name: str,
        file_type: str,
        file_size_bytes: int,
        azure_blob_url: str,
        created_by: str,
        description: Optional[str] = None,
        status: str = "draft",
        tag_ids: Optional[List[UUID]] = None,
        category_ids: Optional[List[UUID]] = None,
        content: Optional[str] = None
    ) -> Template:
        """
        Create a new template.
        
        Args:
            db: Database session
            title: Template title
            file_name: Original file name
            file_type: File extension (docx, pdf, xlsx)
            file_size_bytes: File size in bytes
            azure_blob_url: Azure Blob Storage URL
            created_by: User email
            description: Optional description
            status: Initial status (default: draft)
            tag_ids: List of tag UUIDs to associate
            category_ids: List of category UUIDs to associate
            
        Returns:
            Created template
        """
        template = Template(
            title=title,
            description=description,
            file_name=file_name,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            azure_blob_url=azure_blob_url,
            status=status,
            created_by=created_by,
            updated_by=created_by,
            content=content,
        )
        
        # Add tags
        if tag_ids:
            tags_query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await db.execute(tags_query)
            template.tags = list(result.scalars().all())
        
        # Add categories
        if category_ids:
            cats_query = select(Category).where(Category.id.in_(category_ids))
            result = await db.execute(cats_query)
            template.categories = list(result.scalars().all())
        
        db.add(template)
        # Note: get_db() handles commit automatically after request
        await db.flush()  # Flush to get the ID without committing
        await db.refresh(template)
        
        logger.info(f"Created template: {template.id} - {template.title}")
        return template
    
    @staticmethod
    async def update(
        db: AsyncSession,
        template: Template,
        *,
        updated_by: str,
        **updates
    ) -> Template:
        """
        Update a template.
        
        Args:
            db: Database session
            template: Template to update
            updated_by: User email
            **updates: Fields to update
            
        Returns:
            Updated template
        """
        # Handle special fields
        tag_ids = updates.pop("tag_ids", None)
        category_ids = updates.pop("category_ids", None)
        
        # Update basic fields
        for key, value in updates.items():
            if hasattr(template, key) and value is not None:
                setattr(template, key, value)
        
        template.updated_by = updated_by
        
        # Update tags
        if tag_ids is not None:
            tags_query = select(Tag).where(Tag.id.in_(tag_ids))
            result = await db.execute(tags_query)
            template.tags = list(result.scalars().all())
        
        # Update categories
        if category_ids is not None:
            cats_query = select(Category).where(Category.id.in_(category_ids))
            result = await db.execute(cats_query)
            template.categories = list(result.scalars().all())
        
        # Note: get_db() handles commit automatically after request
        await db.flush()
        await db.refresh(template)
        
        logger.info(f"Updated template: {template.id}")
        return template
    
    @staticmethod
    async def delete(db: AsyncSession, template: Template) -> None:
        """
        Delete a template (soft delete by setting status to archived).
        
        Args:
            db: Database session
            template: Template to delete
        """
        template.status = "archived"
        # Note: get_db() handles commit automatically after request
        await db.flush()
        logger.info(f"Archived template: {template.id}")
    
    @staticmethod
    async def hard_delete(db: AsyncSession, template: Template) -> None:
        """
        Permanently delete a template.
        
        Args:
            db: Database session
            template: Template to delete
        """
        await db.delete(template)
        # Note: get_db() handles commit automatically after request
        await db.flush()
        logger.info(f"Permanently deleted template: {template.id}")

