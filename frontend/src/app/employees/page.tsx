"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Users } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { EmployeeGrid, EmployeeSidebar, EmployeeForm, RoleFilter } from "@/components/employees";

import { useEmployees } from "@/hooks/v3/useEmployees";
import { useOffices } from "@/hooks/v3/useOffices";
import type { EmployeeWithOffice, EmployeeStatus } from "@/types/v3";

export default function EmployeesPage() {
  const router = useRouter();

  const [selectedOfficeId, setSelectedOfficeId] = useState<string | null>(null);
  const [statusFilters, setStatusFilters] = useState<EmployeeStatus[]>(["active", "onboarding", "offboarding"]);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);

  const [editingEmployee, setEditingEmployee] = useState<EmployeeWithOffice | null>(null);

  const { offices, isLoading: officesLoading } = useOffices();
  const { employees, statusCounts, isLoading: employeesLoading, refetch } = useEmployees({
    office_id: selectedOfficeId || undefined,
    status: statusFilters.length > 0 ? statusFilters : undefined,
    role: selectedRole || undefined,
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
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-foreground">Ansatte</h2>
          <p className="text-muted-foreground">
            Oversikt over alle ansatte på tvers av kontorer
          </p>
        </div>

        {/* Main content with sidebar */}
        <div className="flex gap-6">
          <div className="space-y-4">
            <EmployeeSidebar
              offices={offices}
              selectedOfficeId={selectedOfficeId}
              statusFilters={statusFilters}
              statusCounts={statusCounts}
              onOfficeSelect={setSelectedOfficeId}
              onStatusToggle={handleStatusToggle}
            />
            <RoleFilter
              selectedRole={selectedRole}
              onRoleChange={setSelectedRole}
            />
          </div>


          <EmployeeGrid
            employees={employees}
            isLoading={employeesLoading || officesLoading}
            showOffice={!selectedOfficeId}
            onEmployeeClick={handleEmployeeClick}
            onCreateNew={() => setFormOpen(true)}
            onEdit={handleEdit}
            currentFilters={{
              office_id: selectedOfficeId || undefined,
              role: selectedRole || undefined,
            }}
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
      </main>
    </div>
  );
}
