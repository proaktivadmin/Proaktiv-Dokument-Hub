"""
Pydantic schemas for Checklist models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, date
from uuid import UUID


# =============================================================================
# Type Aliases
# =============================================================================

ChecklistType = Literal["onboarding", "offboarding"]
ChecklistStatus = Literal["in_progress", "completed", "cancelled"]


# =============================================================================
# Nested Schemas
# =============================================================================

class ChecklistItem(BaseModel):
    """Schema for a single checklist item."""
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    required: bool = Field(False, description="Whether item is required")
    order: int = Field(0, description="Display order")


class ProgressInfo(BaseModel):
    """Schema for progress information."""
    completed: int = Field(0, description="Number of completed items")
    total: int = Field(0, description="Total number of items")
    percentage: int = Field(0, description="Completion percentage (0-100)")


# =============================================================================
# Template Schemas
# =============================================================================

class ChecklistTemplateBase(BaseModel):
    """Base schema for checklist templates."""
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    type: ChecklistType = Field(..., description="Template type")
    items: List[ChecklistItem] = Field(default_factory=list, description="Checklist items")
    is_active: bool = Field(True, description="Whether template is active")


class ChecklistTemplateCreate(ChecklistTemplateBase):
    """Schema for creating a checklist template."""
    pass


class ChecklistTemplateUpdate(BaseModel):
    """Schema for updating a checklist template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    items: Optional[List[ChecklistItem]] = None
    is_active: Optional[bool] = None


class ChecklistTemplateResponse(ChecklistTemplateBase):
    """Schema for checklist template responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    item_count: int = Field(description="Total number of items")
    required_item_count: int = Field(description="Number of required items")
    
    class Config:
        from_attributes = True


# =============================================================================
# Instance Schemas
# =============================================================================

class ChecklistInstanceBase(BaseModel):
    """Base schema for checklist instances."""
    template_id: UUID = Field(..., description="Template ID")
    employee_id: UUID = Field(..., description="Employee ID")
    due_date: Optional[date] = Field(None, description="Due date")


class ChecklistInstanceCreate(ChecklistInstanceBase):
    """Schema for assigning a checklist to an employee."""
    pass


class ChecklistInstanceUpdateProgress(BaseModel):
    """Schema for updating checklist progress."""
    items_completed: List[str] = Field(..., description="List of completed item names")


class EmployeeMinimal(BaseModel):
    """Minimal employee info for checklist responses."""
    id: UUID
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True


class ChecklistInstanceResponse(ChecklistInstanceBase):
    """Schema for checklist instance responses."""
    id: UUID
    status: ChecklistStatus
    items_completed: List[str]
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    completed_count: int = Field(description="Number of completed items")
    total_count: int = Field(description="Total items from template")
    progress_percentage: int = Field(description="Completion percentage")
    is_completed: bool = Field(description="Whether checklist is completed")
    is_overdue: bool = Field(description="Whether checklist is overdue")
    
    class Config:
        from_attributes = True


class ChecklistInstanceWithDetails(ChecklistInstanceResponse):
    """Schema for checklist instance with template and employee details."""
    template: ChecklistTemplateResponse
    employee: EmployeeMinimal
    progress: ProgressInfo
    
    class Config:
        from_attributes = True


class ChecklistInstanceListResponse(BaseModel):
    """Schema for paginated checklist instance list."""
    items: List[ChecklistInstanceWithDetails]
    total: int
    
    class Config:
        from_attributes = True
