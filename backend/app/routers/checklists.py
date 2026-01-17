"""
Checklists Router - API endpoints for checklist management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.database import get_db
from app.services.checklist_service import ChecklistTemplateService, ChecklistInstanceService
from app.services.employee_service import EmployeeService
from app.schemas.checklist import (
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistTemplateResponse,
    ChecklistInstanceCreate,
    ChecklistInstanceUpdateProgress,
    ChecklistInstanceResponse,
    ChecklistInstanceWithDetails,
    ChecklistInstanceListResponse,
    ProgressInfo,
    EmployeeMinimal,
)

router = APIRouter(prefix="/checklists", tags=["Checklists"])


def _template_to_response(template) -> ChecklistTemplateResponse:
    """Convert ChecklistTemplate model to response schema."""
    return ChecklistTemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        type=template.type,
        items=template.items or [],
        is_active=template.is_active,
        created_at=template.created_at,
        updated_at=template.updated_at,
        item_count=template.item_count,
        required_item_count=template.required_item_count,
    )


def _instance_to_response(instance) -> ChecklistInstanceWithDetails:
    """Convert ChecklistInstance model to response schema with details."""
    completed = instance.completed_count
    total = instance.total_count
    percentage = instance.progress_percentage
    
    return ChecklistInstanceWithDetails(
        id=instance.id,
        template_id=instance.template_id,
        employee_id=instance.employee_id,
        status=instance.status,
        items_completed=instance.items_completed or [],
        due_date=instance.due_date,
        completed_at=instance.completed_at,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        completed_count=completed,
        total_count=total,
        progress_percentage=percentage,
        is_completed=instance.is_completed,
        is_overdue=instance.is_overdue,
        template=_template_to_response(instance.template) if instance.template else None,
        employee=EmployeeMinimal(
            id=instance.employee.id,
            first_name=instance.employee.first_name,
            last_name=instance.employee.last_name,
        ) if instance.employee else None,
        progress=ProgressInfo(
            completed=completed,
            total=total,
            percentage=percentage,
        ),
    )


# =============================================================================
# Template Endpoints
# =============================================================================

@router.get("/templates", response_model=List[ChecklistTemplateResponse])
async def list_templates(
    type: Optional[str] = Query(None, description="Filter by type (onboarding/offboarding)"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all checklist templates.
    """
    templates = await ChecklistTemplateService.list(db, type=type, is_active=is_active)
    return [_template_to_response(t) for t in templates]


@router.post("/templates", response_model=ChecklistTemplateResponse, status_code=201)
async def create_template(
    data: ChecklistTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new checklist template.
    """
    template = await ChecklistTemplateService.create(db, data)
    return _template_to_response(template)


@router.get("/templates/{template_id}", response_model=ChecklistTemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a checklist template by ID.
    """
    template = await ChecklistTemplateService.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return _template_to_response(template)


@router.put("/templates/{template_id}", response_model=ChecklistTemplateResponse)
async def update_template(
    template_id: UUID,
    data: ChecklistTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a checklist template.
    """
    template = await ChecklistTemplateService.update(db, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return _template_to_response(template)


@router.delete("/templates/{template_id}", response_model=ChecklistTemplateResponse)
async def deactivate_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate a checklist template (soft delete).
    """
    template = await ChecklistTemplateService.deactivate(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return _template_to_response(template)


# =============================================================================
# Instance Endpoints
# =============================================================================

@router.get("/instances", response_model=ChecklistInstanceListResponse)
async def list_instances(
    employee_id: Optional[UUID] = Query(None, description="Filter by employee"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all checklist instances with optional filtering.
    
    Status can be: in_progress, completed, cancelled.
    """
    instances, total = await ChecklistInstanceService.list(
        db,
        employee_id=employee_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    
    items = [_instance_to_response(i) for i in instances]
    
    return ChecklistInstanceListResponse(items=items, total=total)


@router.post("/instances", response_model=ChecklistInstanceWithDetails, status_code=201)
async def assign_checklist(
    data: ChecklistInstanceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Assign a checklist to an employee.
    """
    # Verify template exists
    template = await ChecklistTemplateService.get_by_id(db, data.template_id)
    if not template:
        raise HTTPException(status_code=400, detail="Template not found")
    
    # Verify employee exists
    employee = await EmployeeService.get_by_id(db, data.employee_id)
    if not employee:
        raise HTTPException(status_code=400, detail="Employee not found")
    
    instance = await ChecklistInstanceService.create(db, data)
    
    # Reload with relationships
    instance = await ChecklistInstanceService.get_by_id(db, instance.id)
    return _instance_to_response(instance)


@router.get("/instances/{instance_id}", response_model=ChecklistInstanceWithDetails)
async def get_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a checklist instance by ID.
    """
    instance = await ChecklistInstanceService.get_by_id(db, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return _instance_to_response(instance)


@router.put("/instances/{instance_id}", response_model=ChecklistInstanceWithDetails)
async def update_instance_progress(
    instance_id: UUID,
    data: ChecklistInstanceUpdateProgress,
    db: AsyncSession = Depends(get_db),
):
    """
    Update checklist progress.
    
    Provide the list of completed item names.
    If all items are completed, status is automatically set to 'completed'.
    """
    instance = await ChecklistInstanceService.update_progress(db, instance_id, data)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Reload with relationships
    instance = await ChecklistInstanceService.get_by_id(db, instance.id)
    return _instance_to_response(instance)


@router.post("/instances/{instance_id}/cancel", response_model=ChecklistInstanceWithDetails)
async def cancel_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a checklist instance.
    """
    instance = await ChecklistInstanceService.cancel(db, instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Reload with relationships
    instance = await ChecklistInstanceService.get_by_id(db, instance.id)
    return _instance_to_response(instance)
