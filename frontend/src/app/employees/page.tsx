"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Users, ChevronRight, Home } from "lucide-react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { EmployeeGrid, EmployeeSidebar, EmployeeForm } from "@/components/employees";
import { useEmployees } from "@/hooks/v3/useEmployees";
import { useOffices } from "@/hooks/v3/useOffices";
import type { EmployeeWithOffice, EmployeeStatus } from "@/types/v3";

export default function EmployeesPage() {
  const router = useRouter();
  
  const [selectedOfficeId, setSelectedOfficeId] = useState<string | null>(null);
  const [statusFilters, setStatusFilters] = useState<EmployeeStatus[]>(["active", "onboarding", "offboarding"]);
  const [formOpen, setFormOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<EmployeeWithOffice | null>(null);

  const { offices, isLoading: officesLoading } = useOffices();
  const { employees, statusCounts, isLoading: employeesLoading, refetch } = useEmployees({
    office_id: selectedOfficeId || undefined,
    status: statusFilters.length > 0 ? statusFilters : undefined,
  });

  const handleEmployeeClick = (employee: EmployeeWithOffice) => {
    router.push(`/employees/${employee.id}`);
  };

  const handleEdit = (employee: EmployeeWithOffice) => {
    setEditingEmployee(employee);
    setFormOpen(true);
  };

  const handleStatusToggle = (status: EmployeeStatus) => {
    setStatusFilters((prev) =>
      prev.includes(status)
        ? prev.filter((s) => s !== status)
        : [...prev, status]
    );
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingEmployee(null);
  };

  const handleFormSuccess = () => {
    refetch();
    handleFormClose();
  };

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      {/* Breadcrumb */}
      <Breadcrumb className="mb-6">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/" className="flex items-center gap-1">
              <Home className="h-4 w-4" />
              Dashboard
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator>
            <ChevronRight className="h-4 w-4" />
          </BreadcrumbSeparator>
          <BreadcrumbItem>
            <BreadcrumbPage className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              Ansatte
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Ansatte</h1>
        <p className="text-muted-foreground">
          Oversikt over alle ansatte på tvers av kontorer
        </p>
      </div>

      {/* Main content with sidebar */}
      <div className="flex gap-6">
        <EmployeeSidebar
          offices={offices}
          selectedOfficeId={selectedOfficeId}
          statusFilters={statusFilters}
          statusCounts={statusCounts}
          onOfficeSelect={setSelectedOfficeId}
          onStatusToggle={handleStatusToggle}
        />

        <EmployeeGrid
          employees={employees}
          isLoading={employeesLoading || officesLoading}
          showOffice={!selectedOfficeId}
          onEmployeeClick={handleEmployeeClick}
          onCreateNew={() => setFormOpen(true)}
          onEdit={handleEdit}
        />
      </div>

      {/* Form dialog */}
      <EmployeeForm
        open={formOpen}
        onOpenChange={handleFormClose}
        employee={editingEmployee}
        offices={offices}
        defaultOfficeId={selectedOfficeId || undefined}
        onSuccess={handleFormSuccess}
      />
    </div>
  );
}
