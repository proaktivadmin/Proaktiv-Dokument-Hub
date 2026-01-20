"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Header } from "@/components/layout/Header";
import { OfficeGrid, OfficeForm } from "@/components/offices";
import { useOffices } from "@/hooks/v3/useOffices";
import { officesApi } from "@/lib/api/offices";
import { useToast } from "@/hooks/use-toast";
import type { OfficeWithStats } from "@/types/v3";

export default function OfficesPage() {
  const router = useRouter();
  const { offices, cities, isLoading, refetch } = useOffices();
  const { toast } = useToast();
  const [formOpen, setFormOpen] = useState(false);
  const [editingOffice, setEditingOffice] = useState<OfficeWithStats | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleOfficeClick = (office: OfficeWithStats) => {
    router.push(`/offices/${office.id}`);
  };

  const handleEdit = (office: OfficeWithStats) => {
    setEditingOffice(office);
    setFormOpen(true);
  };

  const handleDeactivate = async (office: OfficeWithStats) => {
    if (!confirm(`Er du sikker på at du vil deaktivere "${office.name}"?`)) return;
    
    try {
      await officesApi.deactivate(office.id);
      refetch();
    } catch (err) {
      console.error("Failed to deactivate:", err);
    }
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingOffice(null);
  };

  const handleFormSuccess = () => {
    refetch();
    handleFormClose();
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const result = await officesApi.sync();
      await refetch();
      toast({
        title: "Kontorer synkronisert",
        description: `Oppdatert ${result.synced} av ${result.total} kontorer.`,
      });
    } catch (error) {
      console.error("Failed to sync offices:", error);
      
      // Extract actual error message from backend response
      let errorMessage = "Kunne ikke hente kontorer fra Vitec Hub.";
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

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground">Kontorer</h2>
        <p className="text-muted-foreground">
          Administrer kontorer, ansatte og markedsområder
        </p>
      </div>

      {/* Grid */}
      <OfficeGrid
        offices={offices}
        cities={cities}
        isLoading={isLoading}
        onOfficeClick={handleOfficeClick}
        onCreateNew={() => setFormOpen(true)}
        onSync={handleSync}
        isSyncing={isSyncing}
        onEdit={handleEdit}
        onDeactivate={handleDeactivate}
        onEmployeeClick={(emp) => router.push(`/employees/${emp.id}`)}
      />

      {/* Form dialog */}
      <OfficeForm
        open={formOpen}
        onOpenChange={handleFormClose}
        office={editingOffice}
        onSuccess={handleFormSuccess}
      />
      </main>
    </div>
  );
}
