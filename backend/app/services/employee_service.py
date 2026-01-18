"""
Employee Service - Business logic for employee management.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import logging

from app.models.employee import Employee
from app.models.office import Office
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, StartOffboarding

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for employee CRUD and lifecycle operations."""
    
    @staticmethod
    async def list(
        db: AsyncSession,
        *,
        office_id: Optional[UUID] = None,
        status: Optional[List[str]] = None,
        role: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Employee], int]:
        """
        List employees with optional filtering.
        
        Args:
            db: Database session
            office_id: Filter by office
            status: Filter by status(es)
            role: Filter by Vitec system role
            search: Search by name or email
            skip: Offset for pagination
            limit: Max results
            
        Returns:
            Tuple of (employees, total_count)
        """
        query = select(Employee).options(selectinload(Employee.office))
        count_query = select(func.count()).select_from(Employee)
        
        # Apply filters
        if office_id:
            query = query.where(Employee.office_id == str(office_id))
            count_query = count_query.where(Employee.office_id == str(office_id))
        
        if status:
            query = query.where(Employee.status.in_(status))
            count_query = count_query.where(Employee.status.in_(status))
        
        # Role filter: check if role is in system_roles JSONB array
        if role:
            role_filter = Employee.system_roles.cast(JSONB).contains([role.lower()])
            query = query.where(role_filter)
            count_query = count_query.where(role_filter)
        
        # Search filter: name or email
        if search:
            search_term = f"%{search.lower()}%"
            search_filter = or_(
                func.lower(Employee.first_name).ilike(search_term),
                func.lower(Employee.last_name).ilike(search_term),
                func.lower(Employee.email).ilike(search_term),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Execute count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Execute main query with pagination
        query = query.order_by(Employee.last_name, Employee.first_name).offset(skip).limit(limit)
        result = await db.execute(query)
        employees = list(result.scalars().all())
        
        return employees, total

    
    @staticmethod
    async def get_by_id(db: AsyncSession, employee_id: UUID) -> Optional[Employee]:
        """
        Get an employee by ID with related entities.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            Employee or None
        """
        result = await db.execute(
            select(Employee)
            .options(
                selectinload(Employee.office),
                selectinload(Employee.assets),
                selectinload(Employee.external_listings),
                selectinload(Employee.checklists)
            )
            .where(Employee.id == str(employee_id))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Employee]:
        """
        Get an employee by email.
        
        Args:
            db: Database session
            email: Employee email
            
        Returns:
            Employee or None
        """
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.office))
            .where(Employee.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, data: EmployeeCreate) -> Employee:
        """
        Create a new employee.
        
        Args:
            db: Database session
            data: Employee creation data
            
        Returns:
            Created employee
        """
        employee = Employee(
            office_id=str(data.office_id),
            first_name=data.first_name,
            last_name=data.last_name,
            title=data.title,
            email=data.email,
            phone=data.phone,
            homepage_profile_url=data.homepage_profile_url,
            linkedin_url=data.linkedin_url,
            status=data.status,
            start_date=data.start_date,
            end_date=data.end_date,
            hide_from_homepage_date=data.hide_from_homepage_date,
            delete_data_date=data.delete_data_date,
        )
        db.add(employee)
        await db.flush()
        await db.refresh(employee)
        
        logger.info(f"Created employee: {employee.full_name} ({employee.id})")
        return employee
    
    @staticmethod
    async def update(
        db: AsyncSession,
        employee_id: UUID,
        data: EmployeeUpdate
    ) -> Optional[Employee]:
        """
        Update an existing employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            data: Update data
            
        Returns:
            Updated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Convert office_id to string if present
        if "office_id" in update_data:
            update_data["office_id"] = str(update_data["office_id"])
        
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        await db.flush()
        await db.refresh(employee)
        
        logger.info(f"Updated employee: {employee.full_name} ({employee.id})")
        return employee
    
    @staticmethod
    async def start_offboarding(
        db: AsyncSession,
        employee_id: UUID,
        data: StartOffboarding
    ) -> Optional[Employee]:
        """
        Start the offboarding process for an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            data: Offboarding data
            
        Returns:
            Updated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None
        
        employee.status = "offboarding"
        employee.end_date = data.end_date
        employee.hide_from_homepage_date = data.hide_from_homepage_date
        employee.delete_data_date = data.delete_data_date
        
        await db.flush()
        await db.refresh(employee)
        
        logger.info(f"Started offboarding for: {employee.full_name} ({employee.id})")
        return employee
    
    @staticmethod
    async def deactivate(db: AsyncSession, employee_id: UUID) -> Optional[Employee]:
        """
        Deactivate an employee (mark as inactive).
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            Deactivated employee or None if not found
        """
        employee = await EmployeeService.get_by_id(db, employee_id)
        if not employee:
            return None
        
        employee.status = "inactive"
        await db.flush()
        await db.refresh(employee)
        
        logger.info(f"Deactivated employee: {employee.full_name} ({employee.id})")
        return employee
    
    @staticmethod
    async def get_by_office(
        db: AsyncSession,
        office_id: UUID,
        *,
        status: Optional[List[str]] = None
    ) -> List[Employee]:
        """
        Get all employees for an office.
        
        Args:
            db: Database session
            office_id: Office UUID
            status: Filter by status(es)
            
        Returns:
            List of employees
        """
        query = select(Employee).where(Employee.office_id == str(office_id))
        
        if status:
            query = query.where(Employee.status.in_(status))
        
        query = query.order_by(Employee.last_name, Employee.first_name)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_offboarding_due(db: AsyncSession) -> List[Employee]:
        """
        Get employees with offboarding tasks due.
        
        Returns employees who are offboarding and have dates in the past.
        
        Args:
            db: Database session
            
        Returns:
            List of employees needing attention
        """
        from datetime import date
        today = date.today()
        
        result = await db.execute(
            select(Employee)
            .options(selectinload(Employee.office))
            .where(Employee.status == "offboarding")
            .where(
                (Employee.hide_from_homepage_date <= today) |
                (Employee.delete_data_date <= today)
            )
        )
        return list(result.scalars().all())
