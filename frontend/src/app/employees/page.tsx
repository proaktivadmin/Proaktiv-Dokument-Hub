"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Header } from "@/components/layout/Header";
import {
  EmployeeGrid,
  EmployeeSidebar,
  EmployeeForm,
  RoleFilter,
  EntraSyncDialog,
  EntraSyncBatchDialog,
  SignaturePreviewDialog,
} from "@/components/employees";

import { useEmployees } from "@/hooks/v3/useEmployees";
import { useOffices } from "@/hooks/v3/useOffices";
import { useToast } from "@/hooks/use-toast";
import { employeesApi } from "@/lib/api/employees";
import { officesApi } from "@/lib/api/offices";
import type { EmployeeWithOffice, EmployeeStatus } from "@/types/v3";

export default function EmployeesPage() {
  const router = useRouter();

  const [selectedOfficeId, setSelectedOfficeId] = useState<string | null>(null);
  const [statusFilters, setStatusFilters] = useState<EmployeeStatus[]>(["active"]);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);

  const [editingEmployee, setEditingEmployee] = useState<EmployeeWithOffice | null>(null);

  // Entra sync dialog state
  const [entraSyncEmployee, setEntraSyncEmployee] = useState<EmployeeWithOffice | null>(null);
  const [entraSyncDialogOpen, setEntraSyncDialogOpen] = useState(false);
  const [signaturePreviewEmployee, setSignaturePreviewEmployee] = useState<EmployeeWithOffice | null>(null);
  const [signaturePreviewOpen, setSignaturePreviewOpen] = useState(false);
  const [batchSyncEmployees, setBatchSyncEmployees] = useState<EmployeeWithOffice[]>([]);
  const [batchSyncDialogOpen, setBatchSyncDialogOpen] = useState(false);

  const { toast } = useToast();
  const showInactive = statusFilters.includes("inactive");
  const allStatuses: EmployeeStatus[] = ["active", "onboarding", "offboarding", "inactive"];
  const { offices, isLoading: officesLoading, refetch: refetchOffices } = useOffices(
    showInactive ? undefined : { is_active: true }
  );
  const { employees, statusCounts, isLoading: employeesLoading, refetch: refetchEmployees } = useEmployees({
    office_id: selectedOfficeId || undefined,
    status: statusFilters.length > 0 ? statusFilters : undefined,
    role: selectedRole || undefined,
  });
  const [isSyncing, setIsSyncing] = useState(false);


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

  const handleToggleInactive = () => {
    setStatusFilters((prev) => (prev.includes("inactive") ? ["active"] : allStatuses));
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingEmployee(null);
  };

  const handleFormSuccess = () => {
    refetchEmployees();
    handleFormClose();
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const officeResult = await officesApi.sync();
      const employeeResult = await employeesApi.sync();
      await Promise.all([refetchOffices(), refetchEmployees()]);
      toast({
        title: "Synkronisering fullført",
        description: `Kontorer: ${officeResult.synced}/${officeResult.total}. Ansatte: ${employeeResult.synced}/${employeeResult.total}.`,
      });
    } catch (error) {
      console.error("Failed to sync Vitec Hub data:", error);
      
      // Extract actual error message from backend response
      let errorMessage = "Kunne ikke hente data fra Vitec Hub.";
      if (error instanceof AxiosError && error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Synkronisering feilet",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsSyncing(false);
    }
  };

  // Entra sync handlers
  const handleEntraSync = (employee: EmployeeWithOffice) => {
    setEntraSyncEmployee(employee);
    setEntraSyncDialogOpen(true);
  };

  const handleSignaturePreview = (employee: EmployeeWithOffice) => {
    setSignaturePreviewEmployee(employee);
    setSignaturePreviewOpen(true);
  };

  const handleBatchEntraSync = (employees: EmployeeWithOffice[]) => {
    setBatchSyncEmployees(employees);
    setBatchSyncDialogOpen(true);
  };

  const handleEntraSyncComplete = () => {
    toast({
      title: "Entra ID synkronisering fullført",
      description: entraSyncEmployee
        ? `${entraSyncEmployee.full_name} er oppdatert i Microsoft 365.`
        : "Ansatt er oppdatert.",
    });
    setEntraSyncDialogOpen(false);
    setEntraSyncEmployee(null);
  };

  const handleBatchSyncComplete = (result: { successful: number; failed: number }) => {
    toast({
      title: "Batch synkronisering fullført",
      description: `${result.successful} av ${result.successful + result.failed} ansatte ble synkronisert til Entra ID.`,
    });
    setBatchSyncDialogOpen(false);
    setBatchSyncEmployees([]);
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
            showInactive={showInactive}
            onToggleShowInactive={handleToggleInactive}
            onEmployeeClick={handleEmployeeClick}
            onCreateNew={() => setFormOpen(true)}
            onSync={handleSync}
            isSyncing={isSyncing}
            onEdit={handleEdit}
            currentFilters={{
              office_id: selectedOfficeId || undefined,
              role: selectedRole || undefined,
            }}
            // Entra sync handlers
            onEntraSync={handleEntraSync}
            onSignaturePreview={handleSignaturePreview}
            onBatchEntraSync={handleBatchEntraSync}
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

        {/* Entra sync dialog */}
        <EntraSyncDialog
          employee={entraSyncEmployee}
          open={entraSyncDialogOpen}
          onOpenChange={setEntraSyncDialogOpen}
          onSyncComplete={handleEntraSyncComplete}
          onOpenSignaturePreview={() => {
            if (entraSyncEmployee) {
              handleSignaturePreview(entraSyncEmployee);
            }
          }}
        />

        {/* Signature preview dialog */}
        <SignaturePreviewDialog
          employeeId={signaturePreviewEmployee?.id || null}
          employeeName={signaturePreviewEmployee?.full_name}
          open={signaturePreviewOpen}
          onOpenChange={setSignaturePreviewOpen}
        />

        {/* Batch sync dialog */}
        <EntraSyncBatchDialog
          employees={batchSyncEmployees}
          open={batchSyncDialogOpen}
          onOpenChange={setBatchSyncDialogOpen}
          onSyncComplete={handleBatchSyncComplete}
        />
      </main>
    </div>
  );
}
