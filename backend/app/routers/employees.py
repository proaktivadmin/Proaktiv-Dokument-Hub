"""
Employees Router - API endpoints for employee management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.database import get_db
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeWithOffice,
    EmployeeListResponse,
    StartOffboarding,
    OfficeMinimal,
)

router = APIRouter(prefix="/employees", tags=["Employees"])


def _to_employee_with_office(employee) -> EmployeeWithOffice:
    """Convert Employee model to EmployeeWithOffice schema."""
    return EmployeeWithOffice(
        id=employee.id,
        office_id=employee.office_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        title=employee.title,
        email=employee.email,
        phone=employee.phone,
        homepage_profile_url=employee.homepage_profile_url,
        linkedin_url=employee.linkedin_url,
        status=employee.status,
        start_date=employee.start_date,
        end_date=employee.end_date,
        hide_from_homepage_date=employee.hide_from_homepage_date,
        delete_data_date=employee.delete_data_date,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
        office=OfficeMinimal(
            id=employee.office.id,
            name=employee.office.name,
            short_code=employee.office.short_code,
            color=employee.office.color,
        ) if employee.office else None,
        full_name=employee.full_name,
        initials=employee.initials,
        days_until_end=employee.days_until_end,
    )


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    office_id: Optional[UUID] = Query(None, description="Filter by office"),
    status: Optional[List[str]] = Query(None, description="Filter by status(es)"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all employees with optional filtering.
    
    Status can be: active, onboarding, offboarding, inactive.
    Multiple statuses can be provided.
    """
    employees, total = await EmployeeService.list(
        db,
        office_id=office_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    
    items = [_to_employee_with_office(e) for e in employees]
    
    return EmployeeListResponse(items=items, total=total)


@router.post("", response_model=EmployeeWithOffice, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new employee.
    
    The office_id must reference an existing office.
    """
    # Verify office exists
    office = await OfficeService.get_by_id(db, data.office_id)
    if not office:
        raise HTTPException(status_code=400, detail="Office not found")
    
    employee = await EmployeeService.create(db, data)
    
    # Reload with office relationship
    employee = await EmployeeService.get_by_id(db, employee.id)
    return _to_employee_with_office(employee)


@router.get("/{employee_id}", response_model=EmployeeWithOffice)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get an employee by ID.
    
    Returns the employee with office details.
    """
    employee = await EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return _to_employee_with_office(employee)


@router.put("/{employee_id}", response_model=EmployeeWithOffice)
async def update_employee(
    employee_id: UUID,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an employee.
    
    Only provided fields will be updated.
    """
    # Verify new office exists if changing
    if data.office_id:
        office = await OfficeService.get_by_id(db, data.office_id)
        if not office:
            raise HTTPException(status_code=400, detail="Office not found")
    
    employee = await EmployeeService.update(db, employee_id, data)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Reload with office relationship
    employee = await EmployeeService.get_by_id(db, employee.id)
    return _to_employee_with_office(employee)


@router.post("/{employee_id}/offboarding", response_model=EmployeeWithOffice)
async def start_offboarding(
    employee_id: UUID,
    data: StartOffboarding,
    db: AsyncSession = Depends(get_db),
):
    """
    Start the offboarding process for an employee.
    
    Sets status to 'offboarding' and configures offboarding dates.
    """
    employee = await EmployeeService.start_offboarding(db, employee_id, data)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Reload with office relationship
    employee = await EmployeeService.get_by_id(db, employee.id)
    return _to_employee_with_office(employee)


@router.delete("/{employee_id}", response_model=EmployeeWithOffice)
async def deactivate_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate an employee (soft delete).
    
    Sets status to 'inactive'. Employee data is preserved.
    """
    employee = await EmployeeService.deactivate(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Reload with office relationship
    employee = await EmployeeService.get_by_id(db, employee.id)
    return _to_employee_with_office(employee)


@router.get("/offboarding/due")
async def get_offboarding_due(
    db: AsyncSession = Depends(get_db),
):
    """
    Get employees with overdue offboarding tasks.
    
    Returns employees who are offboarding and have dates in the past.
    """
    employees = await EmployeeService.get_offboarding_due(db)
    return {
        "count": len(employees),
        "employees": [_to_employee_with_office(e) for e in employees],
    }
