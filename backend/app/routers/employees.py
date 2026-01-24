"""
Employees Router - API endpoints for employee management.
"""

from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeSyncResult,
    EmployeeUpdate,
    EmployeeWithOffice,
    OfficeMinimal,
    StartOffboarding,
)
from app.services.employee_service import EmployeeService
from app.services.office_service import OfficeService

router = APIRouter(prefix="/employees", tags=["Employees"])


def _to_employee_with_office(employee) -> EmployeeWithOffice:
    """Convert Employee model to EmployeeWithOffice schema."""
    return EmployeeWithOffice(
        id=employee.id,
        office_id=employee.office_id,
        vitec_employee_id=employee.vitec_employee_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        title=employee.title,
        email=employee.email,
        phone=employee.phone,
        homepage_profile_url=employee.homepage_profile_url,
        linkedin_url=employee.linkedin_url,
        facebook_url=employee.facebook_url,
        instagram_url=employee.instagram_url,
        twitter_url=employee.twitter_url,
        sharepoint_folder_url=employee.sharepoint_folder_url,
        profile_image_url=employee.profile_image_url,
        description=employee.description,
        system_roles=employee.system_roles or [],
        status=employee.status,
        employee_type=employee.employee_type,
        external_company=employee.external_company,
        is_featured_broker=employee.is_featured_broker,
        start_date=employee.start_date,
        end_date=employee.end_date,
        hide_from_homepage_date=employee.hide_from_homepage_date,
        delete_data_date=employee.delete_data_date,
        entra_upn=employee.entra_upn,
        entra_upn_mismatch=employee.entra_upn_mismatch,
        entra_user_id=employee.entra_user_id,
        entra_mail=employee.entra_mail,
        entra_display_name=employee.entra_display_name,
        entra_given_name=employee.entra_given_name,
        entra_surname=employee.entra_surname,
        entra_job_title=employee.entra_job_title,
        entra_mobile_phone=employee.entra_mobile_phone,
        entra_department=employee.entra_department,
        entra_office_location=employee.entra_office_location,
        entra_street_address=employee.entra_street_address,
        entra_postal_code=employee.entra_postal_code,
        entra_country=employee.entra_country,
        entra_account_enabled=employee.entra_account_enabled,
        entra_mismatch_fields=employee.entra_mismatch_fields or [],
        entra_last_synced_at=employee.entra_last_synced_at,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
        office=OfficeMinimal(
            id=employee.office.id,
            name=employee.office.name,
            short_code=employee.office.short_code,
            color=employee.office.color,
        )
        if employee.office
        else None,
        full_name=employee.full_name,
        initials=employee.initials,
        days_until_end=employee.days_until_end,
    )


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    office_id: UUID | None = Query(None, description="Filter by office"),
    status: list[str] | None = Query(None, description="Filter by status(es)"),
    employee_type: list[str] | None = Query(None, description="Filter by employee type(s): internal, external, system"),
    role: str | None = Query(None, description="Filter by Vitec system role"),
    is_featured: bool | None = Query(None, description="Filter by featured status"),
    search: str | None = Query(None, description="Search by name or email"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all employees with optional filtering.

    - **status**: active, onboarding, offboarding, inactive
    - **employee_type**: internal (Proaktiv staff), external (vendors/contractors), system (service accounts)
    - **role**: Vitec Next role (eiendomsmegler, superbruker, etc.)
    - **is_featured**: Filter by featured brokers
    - **search**: Partial match on name or email
    """
    employees, total = await EmployeeService.list(
        db,
        office_id=office_id,
        status=status,
        employee_type=employee_type,
        role=role,
        is_featured=is_featured,
        search=search,
        skip=skip,
        limit=limit,
    )

    items = [_to_employee_with_office(e) for e in employees]

    return EmployeeListResponse(items=items, total=total)


@router.post("/sync", response_model=EmployeeSyncResult)
async def sync_employees(
    db: AsyncSession = Depends(get_db),
):
    """
    Sync employees from Vitec Hub.
    """
    result = await EmployeeService.sync_from_hub(db)
    return EmployeeSyncResult(**result)


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


@router.get("/email-group")
async def get_email_group(
    office_id: UUID | None = Query(None, description="Filter by office"),
    status: list[str] | None = Query(None, description="Filter by status(es)"),
    role: str | None = Query(None, description="Filter by Vitec system role"),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate email group from filtered employees.

    Returns:
    - emails: List of email addresses
    - mailto_link: Ready-to-use mailto: URL
    - count: Number of recipients
    """
    employees, _ = await EmployeeService.list(
        db,
        office_id=office_id,
        status=status or ["active"],  # Default to active employees
        role=role,
        skip=0,
        limit=500,  # Safety limit
    )

    # Extract valid emails
    emails = [e.email for e in employees if e.email]

    if not emails:
        return {
            "emails": [],
            "mailto_link": None,
            "count": 0,
            "message": "No employees with email addresses found",
        }

    # Generate mailto link (semicolon separated for Outlook compatibility)
    mailto_link = f"mailto:{quote(';'.join(emails))}"

    return {
        "emails": emails,
        "mailto_link": mailto_link,
        "count": len(emails),
    }


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
